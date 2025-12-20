from django.db.models import Count
from django.core.cache import cache
from portal.models import Transaction, Book, Profile

def get_recommendations(user, limit=10):
    cache_key = f"recommendations_{user.id}"
    recommendations = cache.get(cache_key)
    if recommendations is not None:
        return recommendations
    """
    Get personalized book recommendations using layered approach:
    - Content-based: Similar department, subject, category
    - Collaborative: Books borrowed by similar users
    - Popularity: Globally popular books
    """
    if not user.is_authenticated or not hasattr(user, 'profile') or user.profile.role != 'student':
        # For non-students or unauthenticated, return popular books
        popular_books = Book.objects.annotate(issue_count=Count('transaction')).order_by('-issue_count')[:limit]
        return popular_books

    borrowed_ids = set(Transaction.objects.filter(user=user).values_list('book_id', flat=True))

    scores = {}

    # Layer 1: Content-based filtering
    dept = user.profile.department
    if dept:
        content_books = Book.objects.filter(department=dept).exclude(id__in=borrowed_ids)
        for book in content_books:
            score = 1  # Department match
            # Check if user borrowed books with same subject
            if Transaction.objects.filter(user=user, book__subject=book.subject).exists():
                score += 3  # Subject similarity
            # Check category similarity (assuming category FK)
            if book.category and Transaction.objects.filter(user=user, book__category=book.category).exists():
                score += 2  # Category similarity
            scores[book.id] = scores.get(book.id, 0) + score * 0.5  # Weighted

    # Layer 2: Collaborative filtering (lightweight co-occurrence)
    common_users = Transaction.objects.filter(book__in=borrowed_ids).exclude(user=user).values_list('user_id', flat=True).distinct()
    if common_users:
        collab_data = Transaction.objects.filter(user__in=common_users).exclude(book_id__in=borrowed_ids).values('book_id').annotate(c=Count('book_id')).order_by('-c')
        for item in collab_data:
            book_id = item['book_id']
            if book_id not in borrowed_ids:
                scores[book_id] = scores.get(book_id, 0) + item['c'] * 0.3  # Weighted co-occurrence

    # Layer 3: Popularity bias
    popular_books = Book.objects.exclude(id__in=borrowed_ids).annotate(issue_count=Count('transaction')).order_by('-issue_count')[:20]
    for book in popular_books:
        scores[book.id] = scores.get(book.id, 0) + book.issue_count * 0.2 / 10  # Normalized weight

    # Layer 4: Department Popularity
    if dept:
        dept_popular_books = Book.objects.filter(department=dept).exclude(id__in=borrowed_ids).annotate(issue_count=Count('transaction')).order_by('-issue_count')[:10]
        for book in dept_popular_books:
            scores[book.id] = scores.get(book.id, 0) + book.issue_count * 0.1  # Weighted for department popularity

    # Rank and return top books
    if scores:
        ranked_ids = sorted(scores, key=scores.get, reverse=True)[:limit]
        recommendations = Book.objects.filter(id__in=ranked_ids).select_related('department', 'category')
    else:
        # Fallback: Department popular or global popular
        if dept:
            recommendations = Book.objects.filter(department=dept).annotate(issue_count=Count('transaction')).order_by('-issue_count')[:limit]
        else:
            recommendations = Book.objects.annotate(issue_count=Count('transaction')).order_by('-issue_count')[:limit]

    return recommendations
