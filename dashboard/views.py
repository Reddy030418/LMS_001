from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Sum
from books.models import Book, Department
from transactions.models import Transaction
from accounts.models import UserProfile
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

@login_required
def dashboard(request):
    if not request.user.is_staff and request.user.userprofile.role != 'librarian':
        return render(request, '403.html')  # Forbidden

    # Stats
    total_books = Book.objects.count()
    total_members = UserProfile.objects.filter(role='student').count()
    active_loans = Transaction.objects.filter(is_returned=False).count()
    overdue_count = Transaction.objects.filter(is_returned=False, due_date__lt=timezone.now().date()).count()

    # Charts data
    issues_per_dept = Transaction.objects.values('book__department__name').annotate(count=Count('id')).order_by('-count')
    active_loans_per_dept = Transaction.objects.filter(is_returned=False).values('book__department__name').annotate(count=Count('id')).order_by('-count')

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'active_loans': active_loans,
        'overdue_count': overdue_count,
        'issues_per_dept': list(issues_per_dept),
        'active_loans_per_dept': list(active_loans_per_dept),
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def export_csv(request):
    if not request.user.is_staff and request.user.userprofile.role != 'librarian':
        return HttpResponse('Forbidden', status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Book', 'Department', 'Issue Date', 'Due Date', 'Return Date', 'Fine'])

    transactions = Transaction.objects.all().select_related('user', 'book__department')
    for t in transactions:
        writer.writerow([
            t.user.username,
            t.book.title,
            t.book.department.name,
            t.issue_date,
            t.due_date,
            t.return_date or '',
            t.fine_amount,
        ])

    return response

@login_required
def export_pdf(request):
    if not request.user.is_staff and request.user.userprofile.role != 'librarian':
        return HttpResponse('Forbidden', status=403)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.drawString(100, height - 50, "Library Transactions Report")

    # Data
    y = height - 100
    transactions = Transaction.objects.all().select_related('user', 'book__department')[:50]  # Limit for demo
    for t in transactions:
        line = f"{t.user.username} - {t.book.title} - {t.book.department.name} - Fine: {t.fine_amount}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
