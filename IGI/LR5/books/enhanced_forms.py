"""
Enhanced forms with proper HTML5 validation and semantic markup.
"""
from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from crispy_forms.bootstrap import PrependedText, AppendedText, FormActions

from .models import (
    Review, Order, CustomerReview, FAQ, Article, Term, 
    Employee, PromoCode, PickupPoint
)


class EnhancedReviewForm(forms.ModelForm):
    """Enhanced review form with proper validation"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} ⭐') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                    'required': True
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Share your thoughts about this book...',
                    'maxlength': 1000,
                    'required': True
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('rating', css_class='mb-3'),
            Field('comment', css_class='mb-3'),
            FormActions(
                Submit('submit', 'Submit Review', css_class='btn btn-primary')
            )
        )


class EnhancedOrderForm(forms.ModelForm):
    """Enhanced order form with delivery options and validation"""
    
    promocode = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter promocode (optional)',
                'pattern': '[A-Z0-9]+',
                'title': 'Promocodes contain only uppercase letters and numbers'
            }
        )
    )
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'delivery_date', 'pickup_point', 'promocode']
        widgets = {
            'shipping_address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter your delivery address...',
                    'required': True
                }
            ),
            'delivery_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'min': timezone.now().date().strftime('%Y-%m-%d')
                }
            ),
            'pickup_point': forms.Select(
                attrs={'class': 'form-select'}
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set pickup point choices
        self.fields['pickup_point'].queryset = PickupPoint.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Delivery Information</h4>'),
            Field('shipping_address', css_class='mb-3'),
            Div(
                Field('delivery_date', css_class='col-md-6'),
                Field('pickup_point', css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Field('promocode', css_class='mb-3'),
            FormActions(
                Submit('submit', 'Place Order', css_class='btn btn-success btn-lg')
            )
        )


class CustomerReviewForm(forms.ModelForm):
    """Form for general customer reviews"""
    
    class Meta:
        model = CustomerReview
        fields = ['rating', 'title', 'text']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} ⭐') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                    'required': True
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Review title...',
                    'maxlength': 200
                }
            ),
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Tell us about your experience...',
                    'maxlength': 2000,
                    'required': True
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('rating', css_class='mb-3'),
            Field('title', css_class='mb-3'),
            Field('text', css_class='mb-3'),
            FormActions(
                Submit('submit', 'Submit Review', css_class='btn btn-primary')
            )
        )


class SearchForm(forms.Form):
    """Enhanced search form with filters"""
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Search books, authors, ISBN...',
                'autocomplete': 'off'
            }
        )
    )
    
    genres = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}
        )
    )
    
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Min price',
                'min': '0',
                'step': '0.01'
            }
        )
    )
    
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Max price',
                'min': '0',
                'step': '0.01'
            }
        )
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
            ('price', 'Price Low-High'),
            ('-price', 'Price High-Low'),
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
        ],
        required=False,
        initial='title',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        from .models import Genre
        super().__init__(*args, **kwargs)
        self.fields['genres'].queryset = Genre.objects.all().order_by('name')
        
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Field('query', css_class='mb-3'),
            HTML('<h6>Filters</h6>'),
            Field('genres', css_class='mb-3'),
            Div(
                Field('min_price', css_class='col-md-6'),
                Field('max_price', css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Field('sort_by', css_class='mb-3'),
            FormActions(
                Submit('submit', 'Search', css_class='btn btn-primary')
            )
        )


class ContactForm(forms.Form):
    """Contact form with validation"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'required': True
            }
        )
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }
        )
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9\s\-\(\)]+$',
                message="Please enter a valid phone number"
            )
        ],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '+375 (XX) XXX-XX-XX',
                'pattern': r'^\+?[0-9\s\-\(\)]+$'
            }
        )
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Message subject',
                'required': True
            }
        )
    )
    
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Your message...',
                'required': True
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('name', css_class='col-md-6'),
                Field('email', css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Field('phone', css_class='col-md-6'),
                Field('subject', css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Field('message', css_class='mb-3'),
            FormActions(
                Submit('submit', 'Send Message', css_class='btn btn-primary')
            )
        )


class NewsletterForm(forms.Form):
    """Newsletter subscription form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email for updates...',
                'required': True
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                Field('email', css_class='flex-grow-1 me-2'),
                Submit('submit', 'Subscribe', css_class='btn btn-outline-primary'),
                css_class='d-flex'
            )
        )


class QuickOrderForm(forms.Form):
    """Quick order form for fast checkout"""
    
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-sm',
                'min': '1',
                'max': '10'
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                PrependedText('quantity', 'Qty:', css_class='input-group-sm me-2'),
                Submit('add_to_cart', 'Add to Cart', css_class='btn btn-primary btn-sm'),
                css_class='d-flex align-items-center'
            )
        )


class PaymentForm(forms.Form):
    """Payment form simulation with validation"""
    
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash on Delivery'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(
            attrs={'class': 'form-check-input'}
        )
    )
    
    card_number = forms.CharField(
        max_length=19,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[0-9\s]+$',
                message="Card number should contain only digits"
            )
        ],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '1234 5678 9012 3456',
                'pattern': '[0-9\s]{13,19}',
                'maxlength': '19'
            }
        )
    )
    
    card_holder = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'JOHN DOE',
                'style': 'text-transform: uppercase'
            }
        )
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^(0[1-9]|1[0-2])/[0-9]{2}$',
                message="Use MM/YY format"
            )
        ],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'MM/YY',
                'pattern': '(0[1-9]|1[0-2])/[0-9]{2}',
                'maxlength': '5'
            }
        )
    )
    
    cvv = forms.CharField(
        max_length=4,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{3,4}$',
                message="CVV should be 3-4 digits"
            )
        ],
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '123',
                'maxlength': '4'
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Payment Method</h5>'),
            Field('payment_method', css_class='mb-4'),
            HTML('<div id="card-details">'),
            HTML('<h6>Card Details</h6>'),
            Field('card_number', css_class='mb-3'),
            Field('card_holder', css_class='mb-3'),
            Div(
                Field('expiry_date', css_class='col-md-6'),
                Field('cvv', css_class='col-md-6'),
                css_class='row mb-3'
            ),
            HTML('</div>'),
            FormActions(
                Submit('submit', 'Complete Payment', css_class='btn btn-success btn-lg')
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'card':
            # Validate card fields when card payment is selected
            required_fields = ['card_number', 'card_holder', 'expiry_date', 'cvv']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for card payments.')
        
        return cleaned_data