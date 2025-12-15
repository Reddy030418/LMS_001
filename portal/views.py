from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Table, Paragraph
from reportlab.lib import colors
import csv
from .models import Book, Department, Transaction, BookRequest, Profile, NewsItem, Eresource
from .forms import BookForm, IssueForm, ReturnForm, BookRequestForm, ProfileForm
from .utils import calculate_fine
from .services.recommender import get_recommendations


def home(request):
    """
    Display home page with book sections, hero search, e-resources, and news.
    """
    # Book sections using flags and filters
    trending_books = Book.objects.filter(is_trending=True)[:10]
    computer_science_books = Book.objects.filter(department__name__icontains='Computer Science')[:8]
    classic_books = Book.objects.filter(subject__icontains='Classic')[:8]
    kids_books = Book.objects.filter(subject__icontains='Children')[:8]
    thriller_books = Book.objects.filter(subject__icontains='Thriller')[:8]
    recently_returned = Book.objects.order_by('-created_at')[:8]  # Proxy for recent returns

    # E-resources (all for home)
    letter = '0'
    if letter == '0':
        eresources = Eresource.objects.filter(letter__regex=r'^[^a-zA-Z]').order_by('name')
    else:
        eresources = Eresource.objects.filter(letter__iexact=letter).order_by('name')

    # News items
    news_items = NewsItem.objects.all()[:3]

    context = {
        'trending_books': trending_books,
        'computer_science_books': computer_science_books,
        'classic_books': classic_books,
        'recently_returned': recently_returned,
        'kids_books': kids_books,
        'thriller_books': thriller_books,
        'eresources': eresources,
        'letter': letter,
        'news_items': news_items,
        'is_home': True,
    }
    return render(request, 'portal/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)
    return render(request, 'portal/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'portal/signup.html', {'form': form})


@login_required
def book_list(request):
    query = request.GET.get('q', '')
    book_type = request.GET.get('type', 'all')
    books = Book.objects.all().order_by('-created_at')

    if query:
        if book_type == 'title':
            books = books.filter(title__icontains=query)
        elif book_type == 'author':
            books = books.filter(author__icontains=query)
        elif book_type == 'subject':
            books = books.filter(subject__icontains=query)
        else:
            books = books.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(subject__icontains=query)
            )

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()
    authors = Book.objects.values_list('author', flat=True).distinct()
    categories = Book.objects.values_list('subject', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'query': query,
        'book_type': book_type,
        'departments': departments,
        'authors': authors,
        'categories': categories,
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    can_request = (
        request.user.is_authenticated and
        book.available_copies > 0 and
        not BookRequest.objects.filter(user=request.user, book=book, status='PENDING').exists() and
        not Transaction.objects.filter(user=request.user, book=book, returned_on__isnull=True).exists()
    )
    pending_request = BookRequest.objects.filter(user=request.user, book=book, status='PENDING').exists()
    active_loan = Transaction.objects.filter(user=request.user, book=book, returned_on__isnull=True).exists()

    # Similar books (content-based)
    similar_books = Book.objects.filter(
        Q(department=book.department) | Q(category=book.category) | Q(subject=book.subject)
    ).exclude(id=book.id).distinct()[:6]

    context = {
        'book': book,
        'can_request': can_request,
        'pending_request': pending_request,
        'active_loan': active_loan,
        'similar_books': similar_books,
    }
    return render(request, 'portal/book_detail.html', context)


@login_required
def my_books(request):
    active_loans = Transaction.objects.filter(user=request.user, returned_on__isnull=True).select_related('book')
    history = Transaction.objects.filter(user=request.user, returned_on__isnull=False).order_by('-returned_on').select_related('book')
    recommendations = get_recommendations(request.user, limit=6)
    context = {
        'active_loans': active_loans,
        'history': history,
        'recommendations': recommendations,
    }
    return render(request, 'portal/my_books.html', context)


@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
        return redirect('home')

    # Currently issued books
    issued_books = Transaction.objects.filter(user=request.user, returned_on__isnull=True).select_related('book')

    # Fine summary
    fine_summary = Transaction.objects.filter(user=request.user, fine_amount__gt=0).aggregate(total=Sum('fine_amount'))['total'] or 0

    # Borrowing history
    history = Transaction.objects.filter(user=request.user).select_related('book').order_by('-issued_on')

    # Recommendations
    recommendations = get_recommendations(request.user, limit=6)

    context = {
        'issued_books': issued_books,
        'fine_summary': fine_summary,
        'history': history,
        'recommendations': recommendations,
    }
    return render(request, 'portal/student_dashboard.html', context)


@login_required
def librarian_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    # Low stock books
    low_stock = Book.objects.filter(available_copies__lte=2).select_related('department')

    # Frequent overdue students
    frequent_overdues = Transaction.objects.filter(fine_amount__gt=0).values('user__username').annotate(overdue_count=Count('id')).order_by('-overdue_count')[:10]

    # Department inventory pressure
    dept_inventory = Book.objects.values('department__name').annotate(
        total=Sum('total_copies'),
        available=Sum('available_copies')
    ).order_by('department__name')

    context = {
        'low_stock': low_stock,
        'frequent_overdues': frequent_overdues,
        'dept_inventory': dept_inventory,
    }
    return render(request, 'portal/librarian_dashboard.html', context)


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    # System KPIs
    total_books = Book.objects.count()
    total_copies = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    active_students = Profile.objects.filter(role='student', is_active_member=True).count()
    total_issues = Transaction.objects.count()
    active_issues = Transaction.objects.filter(returned_on__isnull=True).count()
    overdue_count = Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).count()
    total_fine_collected = Transaction.objects.filter(returned_on__isnull=False, fine_amount__gt=0).aggregate(total=Sum('fine_amount'))['total'] or 0
    pending_fines = Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).aggregate(total=Sum('fine_amount'))['total'] or 0

    # Overdue books
    overdue_books = Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).select_related('book', 'user')[:20]

    # Department-wise issues
    dept_issues = Transaction.objects.values('book__department__name').annotate(issue_count=Count('id')).order_by('-issue_count')

    # Most issued books
    most_issued = Transaction.objects.values('book__title').annotate(total_issues=Count('id')).order_by('-total_issues')[:10]

    # Monthly trends
    monthly_trends = Transaction.objects.annotate(month=TruncMonth('issued_on')).values('month').annotate(count=Count('id')).order_by('month')

    context = {
        'total_books': total_books,
        'total_copies': total_copies,
        'active_students': active_students,
        'total_issues': total_issues,
        'active_issues': active_issues,
        'overdue_count': overdue_count,
        'total_fine_collected': total_fine_collected,
        'pending_fines': pending_fines,
        'overdue_books': overdue_books,
        'dept_issues': dept_issues,
        'most_issued': most_issued,
        'monthly_trends': monthly_trends,
    }
    return render(request, 'portal/admin_dashboard.html', context)


# API Endpoints for Dashboards
@login_required
def dashboard_stats(request):
    if request.user.is_superuser:
        # Admin stats
        data = {
            'total_books': Book.objects.count(),
            'total_copies': Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0,
            'active_students': Profile.objects.filter(role='student', is_active_member=True).count(),
            'total_issues': Transaction.objects.count(),
            'active_issues': Transaction.objects.filter(returned_on__isnull=True).count(),
            'overdue_count': Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).count(),
            'total_fine_collected': Transaction.objects.filter(returned_on__isnull=False, fine_amount__gt=0).aggregate(total=Sum('fine_amount'))['total'] or 0,
            'pending_fines': Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).aggregate(total=Sum('fine_amount'))['total'] or 0,
        }
    elif request.user.is_staff:
        # Librarian stats
        data = {
            'low_stock_count': Book.objects.filter(available_copies__lte=2).count(),
            'overdue_count': Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).count(),
            'pending_requests': BookRequest.objects.filter(status='PENDING').count(),
        }
    else:
        # Student stats
        data = {
            'active_loans': Transaction.objects.filter(user=request.user, returned_on__isnull=True).count(),
            'total_fines': Transaction.objects.filter(user=request.user, fine_amount__gt=0).aggregate(total=Sum('fine_amount'))['total'] or 0,
            'total_borrowed': Transaction.objects.filter(user=request.user).count(),
        }
    return JsonResponse(data)


@login_required
def department_issues_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    data = Transaction.objects.values('book__department__name').annotate(issue_count=Count('id')).order_by('-issue_count')
    return JsonResponse(list(data), safe=False)


@login_required
def monthly_trends_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    data = Transaction.objects.annotate(month=TruncMonth('issued_on')).values('month').annotate(count=Count('id')).order_by('month')
    return JsonResponse(list(data), safe=False)


@login_required
def most_issued_books_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    data = Transaction.objects.values('book__title').annotate(total_issues=Count('id')).order_by('-total_issues')[:10]
    return JsonResponse(list(data), safe=False)


@login_required
def overdue_books_api(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    data = Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).select_related('book', 'user').values(
        'book__title', 'user__username', 'due_date', 'fine_amount'
    )[:20]
    return JsonResponse(list(data), safe=False)


@login_required
def low_stock_books_api(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    data = Book.objects.filter(available_copies__lte=2).select_related('department').values(
        'title', 'available_copies', 'total_copies', 'department__name'
    )
    return JsonResponse(list(data), safe=False)


@login_required
def student_issued_api(request):
    data = Transaction.objects.filter(user=request.user, returned_on__isnull=True).select_related('book').values(
        'book__title', 'due_date', 'fine_amount'
    )
    return JsonResponse(list(data), safe=False)


@login_required
def student_history_api(request):
    data = Transaction.objects.filter(user=request.user).select_related('book').order_by('-issued_on').values(
        'book__title', 'issued_on', 'returned_on', 'fine_amount'
    )[:50]
    return JsonResponse(list(data), safe=False)


@login_required
def request_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookRequestForm(request.POST)
        if form.is_valid():
            book_request = form.save(commit=False)
            book_request.user = request.user
            book_request.book = book
            book_request.save()
            messages.success(request, f'Your request for "{book.title}" has been submitted and is pending approval.')
            return redirect('book_detail', book_id=book_id)
        else:
            messages.error(request, 'There was an error with your request. Please try again.')
    else:
        form = BookRequestForm()
    return redirect('book_detail', book_id=book_id)


@login_required
def issue_book(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            book = transaction.book
            book.available_copies -= 1
            book.save()
            messages.success(request, f'Book "{book.title}" issued successfully!')
            return redirect('my_books')
    else:
        form = IssueForm()
    return render(request, 'portal/issue_book.html', {'form': form})


@login_required
def return_book(request, tx_id):
    transaction = get_object_or_404(Transaction, pk=tx_id, user=request.user)
    if request.method == 'POST':
        returned_date = timezone.localdate()
        transaction.returned_on = returned_date
        transaction.fine = calculate_fine(transaction.due_date, returned_date)
        transaction.save()
        transaction.book.available_copies += 1
        transaction.book.save()
        messages.success(request, f'Book "{transaction.book.title}" returned successfully!')
        return redirect('my_books')
    return render(request, 'portal/return_book.html', {'transaction': transaction})


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_books = Book.objects.count()
    total_users = Profile.objects.count()
    overdue_transactions = Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.localdate()).count()
    active_loans = Transaction.objects.filter(returned_on__isnull=True).count()

    # Issues per department
    issues_per_dept = Transaction.objects.values('book__department__name').annotate(count=Count('id')).order_by('-count')
    issues_data = {
        'labels': [row['book__department__name'] or 'Unknown' for row in issues_per_dept],
        'data': [row['count'] for row in issues_per_dept],
    }

    # Loans per department (active)
    loans_per_dept = Transaction.objects.filter(returned_on__isnull=True).values('book__department__name').annotate(count=Count('id')).order_by('-count')
    loans_data = {
        'labels': [row['book__department__name'] or 'Unknown' for row in loans_per_dept],
        'data': [row['count'] for row in loans_per_dept],
    }

    context = {
        'total_books': total_books,
        'total_members': total_users,
        'active_loans': active_loans,
        'overdue': overdue_transactions,
        'issues_data': issues_data,
        'loans_data': loans_data,
    }
    return render(request, 'portal/admin_dashboard.html', context)


def export_transactions_csv(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    transactions = Transaction.objects.select_related('user', 'book').all()
    if start_date:
        transactions = transactions.filter(issued_on__gte=start_date)
    if end_date:
        transactions = transactions.filter(issued_on__lte=end_date)
    filename = f"transactions_{start_date or 'all'}_{end_date or 'all'}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(['User', 'Book', 'Issue Date', 'Due Date', 'Returned On', 'Fine'])
    for tx in transactions:
        writer.writerow([
            tx.user.username,
            tx.book.title,
            tx.issued_on,
            tx.due_date,
            tx.returned_on or 'Not Returned',
            tx.fine or 0,
        ])
    return response


def export_transactions_pdf(request):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    transactions = Transaction.objects.select_related('user', 'book').all()
    if start_date:
        transactions = transactions.filter(issued_on__gte=start_date)
    if end_date:
        transactions = transactions.filter(issued_on__lte=end_date)
    filename = f"transactions_{start_date or 'all'}_{end_date or 'all'}.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Library Transactions Report", styles['Title']))
    data = [['User', 'Book', 'Issue Date', 'Due Date', 'Returned On', 'Fine']]
    for tx in transactions:
        data.append([
            tx.user.username,
            tx.book.title,
            str(tx.issued_on),
            str(tx.due_date),
            str(tx.returned_on or 'Not Returned'),
            str(tx.fine or 0),
        ])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    doc.build(story)
    return response


def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = Book.objects.filter(
        Q(title__istartswith=query) | Q(author__istartswith=query)
    )[:5].values_list('title', flat=True)
    return JsonResponse(list(suggestions), safe=False)


def search_view(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query) | Q(subject__icontains=query)
    ).order_by('-created_at')
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'results': page_obj.object_list, 'query': query}
    return render(request, 'portal/search_results.html', context)


def advanced_search_view(request):
    if request.method == 'GET':
        title = request.GET.get('title', '')
        author = request.GET.get('author', '')
        department_name = request.GET.get('department', '')
        category_name = request.GET.get('category', '')
        availability = request.GET.get('availability', '')
        books = Book.objects.all()
        if title:
            books = books.filter(title__icontains=title)
        if author:
            books = books.filter(author__icontains=author)
        if department_name:
            books = books.filter(department__name__icontains=department_name)
        if category_name:
            books = books.filter(subject__icontains=category_name)
        if availability == 'available':
            books = books.filter(available_copies__gt=0)
        elif availability == 'issued':
            books = books.filter(available_copies=0)
        paginator = Paginator(books, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        departments = Department.objects.all()
        authors = Book.objects.values_list('author', flat=True).distinct()
        categories = Book.objects.values_list('subject', flat=True).distinct()
        context = {
            "title": title,
            "author": author,
            "department_name": department_name,
            "category_name": category_name,
            "availability": availability,
            "results": books,
            "departments": departments,
            "authors": authors,
            "categories": categories,
        }

        return render(request, "portal/advanced_search.html", context)


@login_required
def my_requests(request):
    requests = BookRequest.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'requests': requests,
    }
    return render(request, 'portal/my_requests.html', context)


@user_passes_test(lambda u: u.is_staff)
def manage_requests(request):
    requests = BookRequest.objects.filter(status='PENDING').order_by('created_at')
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        book_request = get_object_or_404(BookRequest, pk=request_id)
        if action == 'approve':
            # Create transaction
            Transaction.objects.create(
                user=book_request.user,
                book=book_request.book,
                due_date=timezone.localdate() + timezone.timedelta(days=14)
            )
            # Decrease available copies
            book_request.book.available_copies -= 1
            book_request.book.save()
            book_request.status = 'APPROVED'
            book_request.processed_at = timezone.now()
            messages.success(request, f'Request approved for {book_request.book.title}')
        elif action == 'reject':
            book_request.status = 'REJECTED'
            book_request.processed_at = timezone.now()
            messages.success(request, f'Request rejected for {book_request.book.title}')
        book_request.save()
        return redirect('manage_requests')

    context = {
        'requests': requests,
    }
    return render(request, 'portal/manage_requests.html', context)


def eresource_list_view(request, letter):
    """
    Display e-resources starting with the given letter.
    """
    if letter == '0':
        # For non-alphabetic (numbers, symbols)
        eresources = Eresource.objects.filter(letter__regex=r'^[^a-zA-Z]').order_by('name')
    else:
        eresources = Eresource.objects.filter(letter__iexact=letter).order_by('name')

    context = {
        'letter': letter,
        'eresources': eresources,
    }
    return render(request, 'portal/eresources_list.html', context)


def contact(request):
    """
    Display contact details for the library.
    """
    context = {
        'title': 'Contact Us',
        'contact_details': {
            'address': 'Acharya Nagarjuna University Library, Nagarjuna Nagar, Guntur, Andhra Pradesh - 522510',
            'phone': '+91-863-2346200',
            'email': 'library@anu.ac.in',
            'hours': 'Monday - Friday: 8:00 AM - 8:00 PM\nSaturday: 9:00 AM - 5:00 PM\nSunday: Closed',
        }
    }
    return render(request, 'portal/contact.html', context)


def opening_hours(request):
    """
    Display library opening hours for different branches.
    """
    context = {
        'title': 'Opening Hours',
        'hours_data': [
            {'branch': 'Central Library', 'monday_friday': '8:00 AM - 8:00 PM', 'saturday': '9:00 AM - 5:00 PM', 'sunday': 'Closed'},
            {'branch': 'Science Branch', 'monday_friday': '9:00 AM - 6:00 PM', 'saturday': 'Closed', 'sunday': 'Closed'},
            {'branch': 'Arts Branch', 'monday_friday': '8:30 AM - 7:00 PM', 'saturday': '10:00 AM - 4:00 PM', 'sunday': 'Closed'},
        ]
    }
    return render(request, 'portal/opening_hours.html', context)


def ask_librarian(request):
    """
    Display a form for users to ask questions to the librarian.
    """
    if request.method == 'POST':
        # Simple handling: log or send email (placeholder)
        question = request.POST.get('question', '')
        # In production, integrate with email or ticketing system
        messages.success(request, 'Your question has been sent to the librarian. We will respond soon.')
        return redirect('ask_librarian')
    return render(request, 'portal/ask_librarian.html', {'title': 'Ask a Librarian'})


def book_study_room(request):
    """
    Display information and form for booking a study room.
    """
    if request.method == 'POST':
        # Simple handling: log booking request
        date = request.POST.get('date', '')
        time = request.POST.get('time', '')
        messages.success(request, f'Study room booking request for {date} at {time} submitted.')
        return redirect('book_study_room')
    return render(request, 'portal/book_study_room.html', {'title': 'Book a Study Room'})


def news(request):
    """
    Display news and events page.
    """
    news_items = NewsItem.objects.all().order_by('-published_on')
    context = {
        'news_items': news_items,
        'title': 'News & Events'
    }
    return render(request, 'portal/news.html', context)


def department_list(request):
    """
    Display list of all active departments with book statistics and search.
    """
    query = request.GET.get('q', '')
    departments = Department.objects.filter(is_active=True).annotate(
        total_books=Count('book'),
        total_copies=Sum('book__total_copies'),
        available_copies=Sum('book__available_copies'),
        issued_copies=Sum('book__total_copies') - Sum('book__available_copies'),
        active_loans=Count('book__transaction', filter=Q(book__transaction__returned_on__isnull=True)),
        overdue_loans=Count('book__transaction', filter=Q(book__transaction__returned_on__isnull=True, book__transaction__due_date__lt=timezone.now().date()))
    ).order_by('name')

    if query:
        departments = departments.filter(Q(name__icontains=query) | Q(code__icontains=query))

    paginator = Paginator(departments, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'title': 'Departments - ANU LMS'
    }
    return render(request, 'portal/department_list.html', context)


def department_books(request, dept_id):
    """
    Display books for a specific department.
    """
    department = get_object_or_404(Department, pk=dept_id)
    books = Book.objects.filter(department=department).order_by('-created_at')

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'department': department,
        'title': f'Books in {department.name} - ANU LMS'
    }
    return render(request, 'books/book_list.html', context)


def all_search(request):
    """
    Search books by all fields (title, author, subject).
    """
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(subject__icontains=query)
        ).order_by('-created_at')
    else:
        books = Book.objects.none()
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'title': f'Search Results for "{query}"'
    }
    return render(request, 'books/book_list.html', context)


def title_search(request):
    """
    Search books by title.
    """
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        books = Book.objects.none()
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'title': f'Title Search: "{query}"'
    }
    return render(request, 'books/book_list.html', context)


def author_search(request):
    """
    Search books by author.
    """
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(author__icontains=query).order_by('-created_at')
    else:
        books = Book.objects.none()
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'title': f'Author Search: "{query}"'
    }
    return render(request, 'books/book_list.html', context)


def subject_search(request):
    """
    Search books by subject.
    """
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(subject__icontains=query).order_by('-created_at')
    else:
        books = Book.objects.none()
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'title': f'Subject Search: "{query}"'
    }
    return render(request, 'books/book_list.html', context)


def trending_books(request):
    """
    Display trending books page.
    """
    books = Book.objects.filter(is_trending=True).order_by('-created_at')
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Trending Books',
        'is_book_list': True,
    }
    return render(request, 'books/book_list.html', context)


def new_arrivals(request):
    """
    Display new arrivals page.
    """
    books = Book.objects.order_by('-created_at')[:50]
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'New Arrivals',
        'is_book_list': True,
    }
    return render(request, 'books/book_list.html', context)


def rare_books(request):
    """
    Display rare books page.
    """
    books = Book.objects.filter(subject__icontains='Rare').order_by('title')
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Rare Books',
        'is_book_list': True,
    }
    return render(request, 'books/book_list.html', context)


def theses_dissertations(request):
    """
    Display theses and dissertations page.
    """
    books = Book.objects.filter(subject__icontains='Thesis').order_by('title')
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Theses & Dissertations',
        'is_book_list': True,
    }
    return render(request, 'books/book_list.html', context)


def anu_archives(request):
    """
    Display ANU archives page.
    """
    books = Book.objects.filter(subject__icontains='Archive').order_by('title')
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'ANU Archives',
        'is_book_list': True,
    }
    return render(request, 'books/book_list.html', context)
