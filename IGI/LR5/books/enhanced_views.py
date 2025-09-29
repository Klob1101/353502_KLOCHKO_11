"""
Enhanced views implementing all requested features with proper HTML5 semantic markup.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
import logging

from .models import (
    Book, Review, Order, OrderItem, Customer, Genre, Author,
    Banner, Partner, CompanyHistory, CustomerReview, FAQ, 
    Article, Term, Employee, Cart, CartItem, CompanyInfo, PromoCode
)
from .forms import ReviewForm, OrderForm, CustomerReviewForm
from .services import CartService, OrderService, ReviewService, SearchService

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """
    Enhanced homepage with all requested features including:
    - Company logo and banners
    - Service/product catalog
    - Latest article
    - Partners with logos and links
    - Semantic HTML5 markup
    """
    template_name = 'books/home_enhanced.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Company banners for advertisement
        context['banners'] = Banner.objects.filter(is_active=True).order_by('order')[:5]
        
        # Featured books/products catalog
        context['featured_books'] = Book.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(quantity__gt=0).order_by('-created_at')[:8]
        
        # Latest published article
        context['latest_article'] = Article.objects.order_by('-published_at').first()
        
        # Company partners with logos and links
        context['partners'] = Partner.objects.filter(is_active=True).order_by('name')[:12]
        
        # Company basic info
        context['company_info'] = CompanyInfo.objects.first()
        
        # Current date for datetime element
        context['current_date'] = timezone.now()
        
        return context


class BookDetailView(DetailView):
    """
    Enhanced book detail view with:
    - Microdata and semantic markup
    - Reviews and ratings
    - Add to cart functionality
    - Related books
    """
    model = Book
    template_name = 'books/book_detail_enhanced.html'
    context_object_name = 'book'
    
    def get_queryset(self):
        return Book.objects.select_related('publisher').prefetch_related(
            'authors', 'genres', 'reviews'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        
        # Approved reviews for this book
        context['reviews'] = ReviewService.get_book_reviews(book, approved_only=True)
        
        # Review form for authenticated users
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()
            
            # Check if user already reviewed this book
            try:
                customer = self.request.user.customer
                context['user_has_reviewed'] = Review.objects.filter(
                    customer=customer, book=book
                ).exists()
            except Customer.DoesNotExist:
                context['user_has_reviewed'] = False
        
        # Related books (same genre/author)
        related_books = Book.objects.filter(
            Q(genres__in=book.genres.all()) | Q(authors__in=book.authors.all())
        ).exclude(id=book.id).distinct()[:4]
        
        context['related_books'] = related_books
        
        # Structured data for SEO
        context['structured_data'] = {
            'name': book.title,
            'description': book.description,
            'isbn': book.isbn,
            'price': str(book.price),
            'currency': 'BYN',
            'availability': 'InStock' if book.is_available() else 'OutOfStock',
            'rating': book.avg_rating,
            'reviewCount': book.reviews_count
        }
        
        return context


class CartDetailView(TemplateView):
    """
    Enhanced cart view with:
    - Persistent cart using database
    - Quantity management
    - Price calculations
    - Semantic markup
    """
    template_name = 'books/cart_enhanced.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            try:
                customer = self.request.user.customer
                cart = CartService.get_or_create_cart(self.request.user)
                
                context['cart'] = cart
                context['cart_items'] = cart.items.select_related('book').all()
                context['total_cost'] = cart.get_total_cost()
                context['total_items'] = cart.get_total_items()
                
            except Customer.DoesNotExist:
                messages.warning(self.request, 'Please complete your customer profile.')
                context['cart_items'] = []
                context['total_cost'] = Decimal('0.00')
                context['total_items'] = 0
        else:
            context['cart_items'] = []
            context['total_cost'] = Decimal('0.00')
            context['total_items'] = 0
        
        return context


@login_required
def add_to_cart_view(request, book_id):
    """Add book to cart via AJAX or regular request"""
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, 'Please complete your customer profile first.')
        return redirect('users:profile')
    
    result = CartService.add_to_cart(request.user, book, quantity)
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse(result)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('books:book_detail', pk=book_id)


class OrderCreateView(TemplateView):
    """
    Enhanced order creation with:
    - Payment simulation
    - Delivery options
    - Promocode support
    """
    template_name = 'books/order_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            try:
                customer = self.request.user.customer
                cart = CartService.get_or_create_cart(self.request.user)
                
                context['cart'] = cart
                context['cart_items'] = cart.items.select_related('book').all()
                context['total_cost'] = cart.get_total_cost()
                context['form'] = OrderForm()
                
            except Customer.DoesNotExist:
                messages.error(self.request, 'Please complete your customer profile.')
        
        return context
    
    def post(self, request):
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            messages.error(request, 'Customer profile not found.')
            return redirect('users:profile')
        
        form = OrderForm(request.POST)
        if form.is_valid():
            result = OrderService.create_order(
                customer=customer,
                shipping_address=form.cleaned_data['shipping_address'],
                promocode=form.cleaned_data.get('promocode'),
                delivery_date=form.cleaned_data.get('delivery_date'),
                pickup_point_id=form.cleaned_data.get('pickup_point')
            )
            
            if result['success']:
                messages.success(request, 'Order created successfully!')
                return redirect('books:order_detail', pk=result['order'].id)
            else:
                messages.error(request, result['message'])
        
        return self.get(request)


class PaymentView(TemplateView):
    """
    Payment simulation page with:
    - Order summary
    - Payment methods
    - Security features simulation
    """
    template_name = 'books/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        
        if self.request.user.is_authenticated:
            try:
                customer = self.request.user.customer
                order = get_object_or_404(
                    Order, 
                    id=order_id, 
                    customer=customer
                )
                context['order'] = order
                
                # Calculate totals with discounts
                subtotal = order.get_total_cost()
                discount = Decimal('0.00')
                
                if order.promocode:
                    discount = subtotal * (order.promocode.discount_percent / 100)
                
                context['subtotal'] = subtotal
                context['discount'] = discount
                context['total'] = subtotal - discount
                
            except Customer.DoesNotExist:
                messages.error(self.request, 'Customer profile not found.')
        
        return context


class CompanyInfoView(TemplateView):
    """
    About company page with:
    - Company information
    - History by years
    - Video content
    - Certificates
    """
    template_name = 'books/company_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['company_info'] = CompanyInfo.objects.first()
        context['company_history'] = CompanyHistory.objects.all().order_by('-year')
        
        # Sample certificate data (text format as requested)
        context['certificate'] = {
            'number': 'BY/112233445566',
            'issued_date': '2023-01-15',
            'valid_until': '2026-01-15',
            'authority': 'Министерство торговли Республики Беларусь',
            'scope': 'Торговля книгами и сопутствующими товарами'
        }
        
        return context


class NewsListView(ListView):
    """
    News/Articles list with:
    - Pagination
    - Search functionality
    - Article previews
    """
    model = Article
    template_name = 'books/news_list_enhanced.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Article.objects.all().order_by('-published_at')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(summary__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset


class NewsDetailView(DetailView):
    """
    Individual article view with:
    - Full content
    - Related articles
    - Social sharing metadata
    """
    model = Article
    template_name = 'books/news_detail.html'
    context_object_name = 'article'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Related articles
        article = self.object
        related_articles = Article.objects.exclude(
            id=article.id
        ).order_by('-published_at')[:3]
        
        context['related_articles'] = related_articles
        
        return context


class TermsListView(ListView):
    """
    Dictionary of terms and concepts with:
    - Search functionality
    - Alphabetical organization
    - Expandable definitions
    """
    model = Term
    template_name = 'books/terms_list.html'
    context_object_name = 'terms'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Term.objects.all().order_by('term')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(term__icontains=search) |
                Q(definition__icontains=search)
            )
        
        return queryset


class ContactsView(TemplateView):
    """
    Contacts page with:
    - Employee information
    - Contact details
    - Interactive elements
    """
    template_name = 'books/contact_enhanced.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['employees'] = Employee.objects.all().order_by('name')
        
        # Company contact info
        context['company_contacts'] = {
            'phone': '+375 (17) 123-45-67',
            'email': 'info@heavyshop.by',
            'address': 'г. Минск, ул. Примерная, д. 123',
            'working_hours': 'Пн-Пт: 9:00-18:00, Сб: 10:00-16:00'
        }
        
        return context


class VacanciesView(ListView):
    """
    Job vacancies with:
    - Active vacancy listings
    - Job descriptions
    - Application forms
    """
    model = 'Vacancy'
    template_name = 'books/vacancies.html'
    context_object_name = 'vacancies'
    
    def get_queryset(self):
        from .models import Vacancy
        return Vacancy.objects.filter(is_active=True).order_by('-created_at')


class ReviewsView(ListView):
    """
    Customer reviews page with:
    - Review listings
    - Rating displays
    - Review submission form
    """
    model = CustomerReview
    template_name = 'books/reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        return CustomerReview.objects.filter(
            is_approved=True
        ).select_related('customer').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['review_form'] = CustomerReviewForm()
        
        # Average rating
        avg_rating = CustomerReview.objects.filter(
            is_approved=True
        ).aggregate(avg=Avg('rating'))['avg']
        
        context['average_rating'] = avg_rating or 0
        
        return context


@login_required
def add_customer_review(request):
    """Add customer review"""
    if request.method == 'POST':
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            messages.error(request, 'Please complete your customer profile.')
            return redirect('users:profile')
        
        form = CustomerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = customer
            review.save()
            
            messages.success(request, 'Your review has been submitted and is awaiting approval.')
            return redirect('books:reviews')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    
    return redirect('books:reviews')


class PromocodesView(TemplateView):
    """
    Promocodes and coupons page with:
    - Active promocodes
    - Archived promocodes
    - Usage instructions
    """
    template_name = 'books/promocodes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        
        # Active promocodes
        context['active_promocodes'] = PromoCode.objects.filter(
            active=True,
            valid_from__lte=today,
            valid_to__gte=today
        ).order_by('-discount_percent')
        
        # Archived promocodes
        context['archived_promocodes'] = PromoCode.objects.filter(
            Q(active=False) | Q(valid_to__lt=today)
        ).order_by('-valid_to')
        
        return context


class PrivacyPolicyView(TemplateView):
    """
    Privacy policy page with:
    - Legal information
    - Data handling policies
    - User rights
    """
    template_name = 'books/privacy_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['last_updated'] = timezone.now().date()
        
        return context


class FAQView(ListView):
    """
    Frequently Asked Questions with:
    - Categorized questions
    - Search functionality
    - Expandable answers
    """
    model = FAQ
    template_name = 'books/faq.html'
    context_object_name = 'faqs'
    
    def get_queryset(self):
        queryset = FAQ.objects.filter(is_published=True)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(question__icontains=search) |
                Q(answer__icontains=search)
            )
        
        return queryset.order_by('category', 'question')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all categories for filtering
        categories = FAQ.objects.filter(
            is_published=True
        ).values_list('category', flat=True).distinct().exclude(category='')
        
        context['categories'] = sorted(categories)
        context['selected_category'] = self.request.GET.get('category', '')
        
        return context