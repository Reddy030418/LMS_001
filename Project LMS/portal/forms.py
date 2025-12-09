from django import forms
from django.contrib.auth.models import User
from .models import Book, Transaction, BookRequest, Profile

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'department', 'subject', 'isbn', 'publisher', 'rack_number', 'total_copies', 'available_copies', 'cover_image', 'description', 'is_trending', 'is_classic', 'is_romance', 'is_kids', 'is_thriller']


class IssueForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(profile__is_active_member=True), label="Student")
    book = forms.ModelChoiceField(queryset=Book.objects.filter(available_copies__gt=0), label="Book")

    class Meta:
        model = Transaction
        fields = ['user', 'book']


class ReturnForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = []


class BookRequestForm(forms.ModelForm):
    class Meta:
        model = BookRequest
        fields = ['book', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['department', 'student_id']
