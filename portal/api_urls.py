from django.urls import path
from . import api_dashboard

urlpatterns = [
    path("dashboard/issues-per-department/", api_dashboard.chart_issues_per_department),
    path("dashboard/issues-per-month/", api_dashboard.chart_issues_per_month),
    path("dashboard/top-books/", api_dashboard.chart_top_books),
    path("dashboard/active-loans/", api_dashboard.chart_active_loans),
]
