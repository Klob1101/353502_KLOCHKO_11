from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.exceptions import ValidationError
import datetime

User = get_user_model()

class Author(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='authors/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

class Genre(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"

class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name='books')
    genres = models.ManyToManyField(Genre, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='books', null=True, blank=True)
    isbn = models.CharField(max_length=13)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    cover = models.ImageField(upload_to='books/covers/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('books:book_detail', args=[self.id])

    def is_available(self):
        return self.quantity > 0

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
                message="Phone number must be in format: +375 (29) XXX-XX-XX"
            )
        ]
    )
    address = models.TextField()
    birth_date = models.DateField(default=datetime.date(2000, 1, 1))
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone})"

    def clean(self):
        if self.birth_date:
            age = (timezone.now().date() - self.birth_date).days // 365
            if age < 18:
                raise ValidationError('Customer must be at least 18 years old.')
        super().clean()

    def age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_date = models.DateField(null=True, blank=True)
    pickup_point = models.ForeignKey('PickupPoint', null=True, blank=True, on_delete=models.SET_NULL)
    promocode = models.ForeignKey('PromoCode', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity}x {self.book.title}'

    def get_cost(self):
        return self.price * self.quantity

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Review by {self.customer} for {self.book}'

    class Meta:
        ordering = ['-created_at']
        unique_together = ['book', 'customer']

class SalesStatistics(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    best_selling_book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='best_selling_days')
    best_selling_genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='best_selling_days')
    
    class Meta:
        verbose_name = "Sales Statistics"
        verbose_name_plural = "Sales Statistics"
        ordering = ['-date']

    def __str__(self):
        return f"Sales Statistics for {self.date}"

    @classmethod
    def calculate_for_date(cls, date):
        from django.db.models import Sum, Count, Avg
        orders = Order.objects.filter(created_at__date=date)
        
        total_sales = orders.aggregate(Sum('items__price'))['items__price__sum'] or 0
        total_orders = orders.count()
        average_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # Find best selling book
        book_sales = OrderItem.objects.filter(order__created_at__date=date)\
            .values('book')\
            .annotate(total_quantity=Sum('quantity'))\
            .order_by('-total_quantity')
        best_selling_book = None
        if book_sales:
            best_selling_book = Book.objects.get(id=book_sales[0]['book'])
            
        # Find best selling genre
        genre_sales = OrderItem.objects.filter(order__created_at__date=date)\
            .values('book__genres')\
            .annotate(total_quantity=Sum('quantity'))\
            .order_by('-total_quantity')
        best_selling_genre = None
        if genre_sales and genre_sales[0]['book__genres']:
            best_selling_genre = Genre.objects.get(id=genre_sales[0]['book__genres'])
            
        stats, _ = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_sales': total_sales,
                'total_orders': total_orders,
                'average_order_value': average_order_value,
                'best_selling_book': best_selling_book,
                'best_selling_genre': best_selling_genre,
            }
        )
        return stats

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def end_session(self):
        self.end_time = timezone.now()
        self.duration = self.end_time - self.start_time
        self.save()

    @classmethod
    def get_median_duration(cls, start_date=None, end_date=None):
        from statistics import median
        sessions = cls.objects.all()
        if start_date:
            sessions = sessions.filter(start_time__date__gte=start_date)
        if end_date:
            sessions = sessions.filter(start_time__date__lte=end_date)
        
        durations = [s.duration.total_seconds() for s in sessions if s.duration]
        return median(durations) if durations else 0

    def __str__(self):
        return f"Session for {self.user.username} from {self.start_time}"

class PickupPoint(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.address})"

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_to = models.DateField()

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    salary = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    requisites = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-published_at']

class Term(models.Model):
    term = models.CharField(max_length=100)
    definition = models.TextField()
    added_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.term
    class Meta:
        ordering = ['term']

class Employee(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)
    position = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    def __str__(self):
        return self.name
