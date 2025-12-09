from django.urls import path
from . import views

urlpatterns = [
    path('my-requests/', views.my_requests, name='my_requests'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('approve-request/<int:pk>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:pk>/', views.reject_request, name='reject_request'),
]
