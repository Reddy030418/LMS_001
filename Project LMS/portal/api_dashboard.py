from django.http import JsonResponse
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Book, Transaction, Department

def chart_issues_per_department(request):
    data = (
        Transaction.objects
        .values(dept_name=F("book__department__name"))
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = [d["dept_name"] or "Unknown" for d in data]
    values = [d["total"] for d in data]

    return JsonResponse({"labels": labels, "values": values})


def chart_issues_per_month(request):
    year = int(request.GET.get("year", timezone.now().year))

    qs = (
        Transaction.objects.filter(issued_on__year=year)
        .annotate(month=TruncMonth("issued_on"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    labels = [d["month"].strftime("%b") for d in qs]
    values = [d["total"] for d in qs]

    return JsonResponse({"labels": labels, "values": values})


def chart_top_books(request):
    qs = (
        Transaction.objects.values("book__title")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    labels = [b["book__title"] for b in qs]
    values = [b["total"] for b in qs]

    return JsonResponse({"labels": labels, "values": values})


def chart_active_loans(request):
    qs = (
        Transaction.objects.filter(returned_on__isnull=True)
        .values("book__department__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    labels = [x["book__department__name"] or "Unknown" for x in qs]
    values = [x["total"] for x in qs]

    return JsonResponse({"labels": labels, "values": values})
