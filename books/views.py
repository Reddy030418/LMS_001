from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Book, Department
from transactions.models import Transaction, BookRequest

def home(request):
    # Book carousels by categories
    computer_science_books = Book.objects.filter(department__name__icontains='Computer Science')[:10]
    trending_books = Book.objects.order_by('-id')[:10]  # Assuming newer books are trending
    classic_books = Book.objects.filter(subject__icontains='classic')[:10]
    romance_books = Book.objects.filter(subject__icontains='romance')[:10]
    kids_books = Book.objects.filter(subject__icontains='kids')[:10]
    thriller_books = Book.objects.filter(subject__icontains='thriller')[:10]
    recently_returned = Book.objects.filter(available_copies__gt=0).order_by('-id')[:10]  # Placeholder

    total_books = Book.objects.count()
    available_books = Book.objects.filter(available_copies__gt=0).count()
    active_users = 0  # Placeholder

    book_sections = {
        'Computer Science': computer_science_books,
        'Trending Books': trending_books,
        'Classic Books': classic_books,
        'Romance': romance_books,
        'Kids': kids_books,
        'Thriller': thriller_books,
        'Recently Returned': recently_returned,
    }

    context = {
        'book_sections': book_sections,
        'total_books': total_books,
        'available_books': available_books,
        'active_users': active_users,
    }
    return render(request, 'home.html', context)

def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 12)  # Show 12 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/book_list.html', {'page_obj': page_obj})

def search(request):
    query = request.GET.get('q')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(subject__icontains=query)
        )
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/search_results.html', {'page_obj': page_obj, 'query': query})

@login_required
def book_create(request):
    if not request.user.userprofile.role == 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can add books.')
        return redirect('book_list')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Add Book'})

@login_required
def book_update(request, pk):
    if not request.user.userprofile.role == 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can edit books.')
        return redirect('book_list')

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Edit Book'})

@login_required
def book_delete(request, pk):
    if not request.user.userprofile.role == 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can delete books.')
        return redirect('book_list')

    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})

@login_required
def request_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.user.userprofile.role != 'student':
        messages.error(request, 'Only students can request books.')
        return redirect('book_detail', pk=pk)

    # Check if user already has a pending request for this book
    existing_request = BookRequest.objects.filter(user=request.user, book=book, status='pending').exists()
    if existing_request:
        messages.warning(request, 'You already have a pending request for this book.')
        return redirect('book_detail', pk=pk)

    # Check if user already has this book issued
    active_transaction = Transaction.objects.filter(user=request.user, book=book, is_returned=False).exists()
    if active_transaction:
        messages.warning(request, 'You already have this book issued.')
        return redirect('book_detail', pk=pk)

    if book.available_copies > 0:
        BookRequest.objects.create(user=request.user, book=book)
        messages.success(request, 'Book request submitted successfully.')
    else:
        messages.error(request, 'Book is not available.')

    return redirect('book_detail', pk=pk)

@login_required
def issue_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.user.userprofile.role != 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can issue books.')
        return redirect('book_detail', pk=pk)

    if book.available_copies <= 0:
        messages.error(request, 'No copies available to issue.')
        return redirect('book_detail', pk=pk)

    # Check if user already has this book issued
    active_transaction = Transaction.objects.filter(user=request.user, book=book, is_returned=False).exists()
    if active_transaction:
        messages.warning(request, 'User already has this book issued.')
        return redirect('book_detail', pk=pk)

    # Create transaction
    due_date = datetime.now().date() + timedelta(days=14)  # 14 days loan period
    Transaction.objects.create(
        user=request.user,
        book=book,
        due_date=due_date
    )
    book.available_copies -= 1
    book.save()
    messages.success(request, f'Book issued successfully. Due date: {due_date}')
    return redirect('book_detail', pk=pk)

@login_required
def return_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.user.userprofile.role != 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can return books.')
        return redirect('book_detail', pk=pk)

    # Find active transaction for this book
    try:
        transaction = Transaction.objects.get(user=request.user, book=book, is_returned=False)
    except Transaction.DoesNotExist:
        messages.error(request, 'No active transaction found for this book.')
        return redirect('book_detail', pk=pk)

    # Mark transaction as returned
    transaction.return_date = datetime.now()
    transaction.is_returned = True
    transaction.calculate_fine()
    transaction.save()

    # Increase available copies
    book.available_copies += 1
    book.save()

    messages.success(request, f'Book returned successfully. Fine: ${transaction.fine_amount}')
    return redirect('book_detail', pk=pk)
