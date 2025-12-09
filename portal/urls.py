from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('my-books/', views.my_books, name='my_books'),
    path('issue-book/', views.issue_book, name='issue_book'),
    path('return-book/<int:tx_id>/', views.return_book, name='return_book'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export/csv/', views.export_transactions_csv, name='export_csv'),
    path('export/pdf/', views.export_transactions_pdf, name='export_pdf'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('search/', views.search_view, name='search'),
    path('search/advanced/', views.advanced_search_view, name='advanced_search'),
    path('eresources/<str:letter>/', views.eresource_list_view, name='eresources_list'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('contact/', views.contact, name='contact'),
]
