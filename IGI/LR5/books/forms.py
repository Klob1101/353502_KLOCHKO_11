from django import forms
from django.core.validators import MinValueValidator
from .models import Customer, Book, Review, Order, PickupPoint, Vacancy
from django.utils import timezone

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+375 (29) XXX-XX-XX', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            age = (timezone.now().date() - birth_date).days // 365
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old.')
        return birth_date

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'genres', 'publisher', 'isbn', 'description',
                 'price', 'quantity', 'cover']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    delivery_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    pickup_point = forms.ModelChoiceField(queryset=PickupPoint.objects.filter(is_active=True), required=False)
    promocode = forms.CharField(required=False, max_length=20, label='Promo code')

    class Meta:
        model = Order
        fields = ['delivery_date', 'pickup_point']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
        }

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'requirements', 'salary', 'is_active'] 