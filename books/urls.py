from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('search/', views.search, name='search'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('books/<int:pk>/request/', views.request_book, name='request_book'),
    path('books/<int:pk>/issue/', views.issue_book, name='issue_book'),
    path('books/<int:pk>/return/', views.return_book, name='return_book'),
]
