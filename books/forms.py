from django import forms
from .models import Book, Department

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'description', 'department', 'total_copies', 'available_copies', 'cover_image', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'cover_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
