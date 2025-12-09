from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import BookRequest, Transaction
from books.models import Book

@login_required
def my_requests(request):
    if request.user.userprofile.role != 'student':
        messages.error(request, 'Only students can view their requests.')
        return redirect('home')

    requests = BookRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/my_requests.html', {'requests': requests})

@login_required
def manage_requests(request):
    if request.user.userprofile.role != 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can manage requests.')
        return redirect('home')

    requests = BookRequest.objects.filter(status='pending').order_by('created_at')
    return render(request, 'transactions/manage_requests.html', {'requests': requests})

@login_required
def approve_request(request, pk):
    if request.user.userprofile.role != 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can approve requests.')
        return redirect('manage_requests')

    book_request = get_object_or_404(BookRequest, pk=pk)
    if book_request.status != 'pending':
        messages.error(request, 'Request is not pending.')
        return redirect('manage_requests')

    # Check if book is available
    if book_request.book.available_copies <= 0:
        messages.error(request, 'Book is not available.')
        return redirect('manage_requests')

    # Approve request and issue book
    book_request.status = 'approved'
    book_request.processed_at = timezone.now()
    book_request.save()

    # Create transaction
    due_date = timezone.now().date() + timedelta(days=14)
    Transaction.objects.create(
        user=book_request.user,
        book=book_request.book,
        due_date=due_date
    )
    book_request.book.available_copies -= 1
    book_request.book.save()

    messages.success(request, f'Request approved and book issued. Due date: {due_date}')
    return redirect('manage_requests')

@login_required
def reject_request(request, pk):
    if request.user.userprofile.role != 'librarian' and not request.user.is_staff:
        messages.error(request, 'Only librarians can reject requests.')
        return redirect('manage_requests')

    book_request = get_object_or_404(BookRequest, pk=pk)
    if book_request.status != 'pending':
        messages.error(request, 'Request is not pending.')
        return redirect('manage_requests')

    book_request.status = 'rejected'
    book_request.processed_at = timezone.now()
    book_request.save()

    messages.success(request, 'Request rejected.')
    return redirect('manage_requests')
