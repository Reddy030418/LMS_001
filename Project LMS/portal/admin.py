from django.contrib import admin
from .models import Book, Department, Transaction, BookRequest, Profile, NewsItem, Eresource

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'department', 'available_copies', 'total_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('department', 'is_trending', 'is_classic', 'is_romance', 'is_kids', 'is_thriller')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'issued_on', 'due_date', 'returned_on', 'fine_amount')
    search_fields = ('user__username', 'book__title')
    list_filter = ('issued_on', 'returned_on')

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'created_at', 'processed_at')
    search_fields = ('user__username', 'book__title')
    list_filter = ('status', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'student_id', 'is_active_member')
    search_fields = ('user__username', 'student_id')
    list_filter = ('department', 'is_active_member')

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_on')
    search_fields = ('title', 'summary')
    list_filter = ('published_on',)

@admin.register(Eresource)
class EresourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'letter', 'url')
    search_fields = ('name',)
    list_filter = ('letter',)
