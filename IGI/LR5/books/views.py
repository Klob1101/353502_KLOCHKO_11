from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum, F
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone
from django.utils.decorators import method_decorator
from .models import Book, Review, Order, OrderItem, Customer, Genre, SalesStatistics, PromoCode, Vacancy, Article, CompanyInfo, Term, Employee
from .forms import ReviewForm, OrderForm, VacancyForm
from .decorators import staff_required
import logging
from datetime import datetime, timedelta
from statistics import median, mode
from collections import defaultdict
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')  # Для headless-режима
import matplotlib.pyplot as plt
import os
import json
import statistics
from django.contrib.admin.views.decorators import staff_member_required
import requests
import calendar

logger = logging.getLogger(__name__)

def book_list(request):
    books = Book.objects.all().annotate(avg_rating=Avg('reviews__rating'))
    genres = Genre.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(authors__name__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(genres__name__icontains=search_query)
        ).distinct()
        logger.info(f'Search query: {search_query}, Results: {books.count()}')

    # Genre filter
    genre_id = request.GET.get('genre')
    if genre_id:
        books = books.filter(genres__id=genre_id)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)

    # Sorting
    sort_by = request.GET.get('sort', 'title')
    if sort_by in ['title', '-title', 'price', '-price', 'avg_rating', '-avg_rating']:
        books = books.order_by(sort_by)

    return render(request, 'books/book_list.html', {
        'books': books,
        'genres': genres,
        'search_query': search_query,
        'selected_genre': genre_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by
    })

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.filter(is_approved=True)
    review_form = ReviewForm()
    return render(request, 'books/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'review_form': review_form
    })

@login_required
def add_review(request, pk):
    book = get_object_or_404(Book, pk=pk)
    customer = request.user.customer
    if request.method == 'POST':
        if Review.objects.filter(book=book, customer=customer).exists():
            messages.error(request, 'Вы уже оставили отзыв на эту книгу.')
            return redirect('books:book_detail', pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.customer = customer
            review.save()
            messages.success(request, 'Ваш отзыв отправлен на модерацию.')
            return redirect('books:book_detail', pk=pk)
    return redirect('books:book_detail', pk=pk)

@login_required
def cart_detail(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.warning(request, 'Please complete your profile before using the cart.')
        return redirect('users:profile')
        
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, id=book_id)
        total += book.price * Decimal(quantity)
        cart_items.append({
            'book': book,
            'quantity': quantity,
            'total': book.price * Decimal(quantity)
        })
    return render(request, 'books/cart_detail.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def cart_add(request, book_id):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.warning(request, 'Please complete your profile before adding items to cart.')
        return redirect('users:profile')
        
    cart = request.session.get('cart', {})
    book = get_object_or_404(Book, id=book_id)
    
    if str(book_id) in cart:
        if book.quantity > cart[str(book_id)]:
            cart[str(book_id)] += 1
            messages.success(request, f'Added one more "{book.title}" to your cart.')
        else:
            messages.error(request, 'Sorry, we don\'t have enough books in stock.')
    else:
        if book.quantity > 0:
            cart[str(book_id)] = 1
            messages.success(request, f'Added "{book.title}" to your cart.')
        else:
            messages.error(request, 'Sorry, this book is out of stock.')
    
    request.session['cart'] = cart
    return redirect('books:cart_detail')

@login_required
def cart_remove(request, book_id):
    cart = request.session.get('cart', {})
    if str(book_id) in cart:
        del cart[str(book_id)]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart.')
    return redirect('books:cart_detail')

@login_required
def order_create(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.warning(request, 'Please complete your profile before placing orders.')
        return redirect('users:profile')
        
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('books:cart_detail')

    # Формируем список товаров и сумму для Order Summary
    cart_items = []
    total = 0
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, id=book_id)
        item_total = book.price * Decimal(quantity)
        total += item_total
        cart_items.append({
            'book': book,
            'quantity': quantity,
            'total': item_total
        })

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            # обработка промокода
            promocode_str = form.cleaned_data.get('promocode')
            discount = 0
            if promocode_str:
                today = timezone.now().date()
                try:
                    promocode_obj = PromoCode.objects.get(code=promocode_str, active=True, valid_from__lte=today, valid_to__gte=today)
                    order.promocode = promocode_obj
                    discount = promocode_obj.discount_percent
                except PromoCode.DoesNotExist:
                    messages.warning(request, 'Promo code is invalid or expired.')
            # order.promocode не трогаем, если промокод не найден или не введён
            order.save()

            for book_id, quantity in cart.items():
                book = get_object_or_404(Book, id=book_id)
                if book.quantity >= quantity:
                    price = book.price
                    OrderItem.objects.create(
                        order=order,
                        book=book,
                        quantity=quantity,
                        price=price
                    )
                    book.quantity -= quantity
                    book.save()
                else:
                    order.delete()
                    messages.error(request, f'Sorry, {book.title} is out of stock.')
                    return redirect('books:cart_detail')
            # применяем скидку
            if discount:
                total = total * (1 - discount / 100)
            order.delivery_date = form.cleaned_data.get('delivery_date')
            order.pickup_point = form.cleaned_data.get('pickup_point')
            order.save()
            request.session['cart'] = {}
            messages.success(request, 'Your order has been placed successfully.')
            return redirect('books:order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'books/order_form.html', {'form': form, 'cart_items': cart_items, 'total': total})

@login_required
def order_detail(request, pk):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.warning(request, 'Please complete your profile before viewing orders.')
        return redirect('users:profile')
        
    order = get_object_or_404(Order, pk=pk, customer=customer)
    return render(request, 'books/order_detail.html', {'order': order})

@login_required
def order_list(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.warning(request, 'Please complete your profile before viewing orders.')
        return redirect('users:profile')
        
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'books/order_list.html', {'orders': orders})

class StatisticsView(TemplateView):
    template_name = 'books/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Общая статистика по продажам
        total_sales = OrderItem.objects.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0
        
        # Список всех продаж для расчета медианы
        all_sales = list(OrderItem.objects.values_list(
            F('quantity') * F('price'), flat=True
        ))
        
        # Статистика по возрасту клиентов
        today = timezone.now().date()
        customer_ages = [
            (today - customer.birth_date).days // 365
            for customer in Customer.objects.all()
            if customer.birth_date
        ]
        
        # Популярные жанры
        popular_genres = Book.objects.values('genres__name').annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:5]
        
        # Прибыльные жанры
        profitable_genres = Book.objects.values('genres__name').annotate(
            total_profit=Sum(F('orderitem__quantity') * F('orderitem__price'))
        ).order_by('-total_profit')[:5]
        
        context.update({
            'total_sales': total_sales,
            'avg_sale': statistics.mean(all_sales) if all_sales else 0,
            'median_sale': statistics.median(all_sales) if all_sales else 0,
            'avg_customer_age': statistics.mean(customer_ages) if customer_ages else 0,
            'median_customer_age': statistics.median(customer_ages) if customer_ages else 0,
            'popular_genres': popular_genres,
            'profitable_genres': profitable_genres,
        })
        # Генерируем график продаж по месяцам
        sales_img_url = self.generate_sales_by_month_chart()
        context['sales_by_month_img'] = sales_img_url
        # Генерируем график продаж по жанрам
        genre_img_url = self.generate_sales_by_genre_chart()
        context['sales_by_genre_img'] = genre_img_url
        return context
    
    def get_sales_by_month(self):
        current_year = timezone.now().year
        sales_by_month = OrderItem.objects.filter(
            order__created_at__year=current_year
        ).values('order__created_at__month').annotate(
            total=Sum(F('quantity') * F('price'))
        ).order_by('order__created_at__month')
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = [0] * 12
        for sale in sales_by_month:
            month_idx = sale['order__created_at__month'] - 1
            data[month_idx] = float(sale['total'])
        return {'labels': months, 'data': data, 'year': current_year}

    def generate_sales_by_month_chart(self):
        sales = self.get_sales_by_month()
        months = sales['labels']
        data = sales['data']
        year = sales['year']
        plt.figure(figsize=(8, 4))
        plt.bar(months, data, color='#007bff')
        plt.title(f'Sales by Month ({year})')
        plt.xlabel('Month')
        plt.ylabel('Sales (BYN)')
        plt.tight_layout()
        img_dir = os.path.join('static', 'images', 'stats')
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, 'sales_by_month.png')
        plt.savefig(img_path)
        plt.close()
        return 'images/stats/sales_by_month.png'

    def generate_sales_by_genre_chart(self):
        from django.db.models import Sum
        genre_sales = Book.objects.values('genres__name').annotate(
            total=Sum('orderitem__quantity')
        ).order_by('-total')
        labels = [g['genres__name'] or 'Unknown' for g in genre_sales if g['genres__name']]
        data = [g['total'] or 0 for g in genre_sales if g['genres__name']]
        if not labels:
            labels = ['No data']
            data = [0]
        plt.figure(figsize=(8, 4))
        plt.bar(labels, data, color='#28a745')
        plt.title('Sales by Genre')
        plt.xlabel('Genre')
        plt.ylabel('Books Sold')
        plt.tight_layout()
        img_dir = os.path.join('static', 'images', 'stats')
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, 'sales_by_genre.png')
        plt.savefig(img_path)
        plt.close()
        return 'images/stats/sales_by_genre.png'

@staff_member_required
def moderate_reviews(request):
    from .models import Review
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        action = request.POST.get('action')
        review = get_object_or_404(Review, id=review_id, is_approved=False)
        if action == 'approve':
            review.is_approved = True
            review.save()
            messages.success(request, 'Review approved.')
        elif action == 'reject':
            review.delete()
            messages.success(request, 'Review rejected and deleted.')
        return redirect('books:moderate_reviews')
    reviews = Review.objects.filter(is_approved=False).order_by('-created_at')
    return render(request, 'books/moderate_reviews.html', {'reviews': reviews})

def is_staff(user):
    return user.is_staff

def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'books/vacancy_list.html', {'vacancies': vacancies})

@user_passes_test(is_staff)
def vacancy_create(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vacancy created.')
            return redirect('books:vacancy_list')
    else:
        form = VacancyForm()
    return render(request, 'books/vacancy_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_staff)
def vacancy_update(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vacancy updated.')
            return redirect('books:vacancy_list')
    else:
        form = VacancyForm(instance=vacancy)
    return render(request, 'books/vacancy_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_staff)
def vacancy_delete(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        vacancy.delete()
        messages.success(request, 'Vacancy deleted.')
        return redirect('books:vacancy_list')
    return render(request, 'books/vacancy_confirm_delete.html', {'vacancy': vacancy})

def home(request):
    last_article = Article.objects.order_by('-published_at').first()
    weather = None
    weather_error = None
    try:
        resp = requests.get('https://api.open-meteo.com/v1/forecast?latitude=53.9&longitude=27.5667&current_weather=true')
        if resp.status_code == 200:
            data = resp.json()
            weather = {
                'temp': data['current_weather']['temperature'],
                'windspeed': data['current_weather']['windspeed'],
                'desc': 'Current weather in Minsk'
            }
        else:
            weather_error = f"Weather API error: {resp.status_code}"
            logger.warning(weather_error)
    except Exception as e:
        weather_error = f"Weather API exception: {e}"
        logger.error(weather_error)
    currency = None
    currency_error = None
    try:
        resp = requests.get('https://api.frankfurter.app/latest?from=USD&to=PLN,EUR')
        if resp.status_code == 200:
            data = resp.json()
            if 'rates' in data:
                currency = {
                    'usd_pln': data['rates'].get('PLN'),
                    'usd_eur': data['rates'].get('EUR')
                }
            else:
                currency_error = f"Currency API: no 'rates' in response: {data}"
                logger.warning(currency_error)
        else:
            currency_error = f"Currency API error: {resp.status_code}"
            logger.warning(currency_error)
    except Exception as e:
        currency_error = f"Currency API exception: {e}"
        logger.error(currency_error)
    # Календарь на текущий месяц
    now = timezone.now()
    cal = calendar.TextCalendar(firstweekday=0)
    text_calendar = cal.formatmonth(now.year, now.month)
    month_name = now.strftime('%B')
    year = now.year
    return render(request, 'books/home.html', {
        'last_article': last_article,
        'weather': weather,
        'currency': currency,
        'weather_error': weather_error,
        'currency_error': currency_error,
        'text_calendar': text_calendar,
        'month_name': month_name,
        'year': year,
    })

def company_info(request):
    info = CompanyInfo.objects.first()
    return render(request, 'books/company_info.html', {'info': info})

def news_list(request):
    articles = Article.objects.order_by('-published_at')
    return render(request, 'books/news_list.html', {'articles': articles})

def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'books/news_detail.html', {'article': article})

def terms_list(request):
    terms = Term.objects.order_by('term')
    return render(request, 'books/terms_list.html', {'terms': terms})

def contacts(request):
    employees = Employee.objects.all()
    return render(request, 'books/contacts.html', {'employees': employees})

def privacy_policy(request):
    return render(request, 'books/privacy_policy.html')

def promocode_list(request):
    from .models import PromoCode
    today = timezone.now().date()
    active = PromoCode.objects.filter(active=True, valid_from__lte=today, valid_to__gte=today)
    archive = PromoCode.objects.filter(active=False) | PromoCode.objects.filter(valid_to__lt=today)
    return render(request, 'books/promocode_list.html', {'active': active, 'archive': archive})

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, customer=request.user.customer)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш отзыв обновлён.')
            return redirect('books:book_detail', pk=review.book.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'books/edit_review.html', {'form': form, 'review': review})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, customer=request.user.customer)
    book_pk = review.book.pk
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Ваш отзыв удалён.')
        return redirect('books:book_detail', pk=book_pk)
    return render(request, 'books/delete_review_confirm.html', {'review': review})


def html5_showcase(request):
    """HTML5 Features Showcase page."""
    return render(request, 'books/html5_showcase.html', {})