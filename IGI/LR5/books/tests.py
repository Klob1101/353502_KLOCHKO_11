from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from .models import Book, Author, Genre, Publisher, Customer, Order, OrderItem, Review, SalesStatistics
from decimal import Decimal
from django.core.exceptions import ValidationError
import datetime

User = get_user_model()

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовые данные
        cls.author = Author.objects.create(
            name='Test Author'
        )
        cls.genre = Genre.objects.create(name='Test Genre')
        cls.publisher = Publisher.objects.create(name='Test Publisher')
        cls.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            price=Decimal('29.99'),
            quantity=10,
            publisher=cls.publisher
        )
        cls.book.authors.add(cls.author)
        cls.book.genres.add(cls.genre)

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test Book')

    def test_book_get_absolute_url(self):
        self.assertEqual(
            self.book.get_absolute_url(),
            reverse('books:book_detail', args=[self.book.id])
        )

    def test_book_is_available(self):
        self.assertTrue(self.book.is_available())
        self.book.quantity = 0
        self.book.save()
        self.assertFalse(self.book.is_available())

class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67'
        )

    def test_customer_str(self):
        self.assertEqual(str(self.customer), 'testuser')

    def test_phone_number_validation(self):
        # Valid phone number
        customer = Customer(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=datetime.date(1990, 1, 1)
        )
        customer.full_clean()  # Should not raise ValidationError

        # Invalid phone number
        with self.assertRaises(ValidationError):
            customer = Customer(
                user=self.user,
                phone='123456789',  # Invalid format
                address='Test Address',
                birth_date=datetime.date(1990, 1, 1)
            )
            customer.full_clean()

    def test_age_restriction(self):
        # Customer over 18
        customer = Customer(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=timezone.now().date() - datetime.timedelta(days=365*20)
        )
        customer.full_clean()  # Should not raise ValidationError

        # Customer under 18
        with self.assertRaises(ValidationError):
            customer = Customer(
                user=self.user,
                phone='+375 (29) 123-45-67',
                address='Test Address',
                birth_date=timezone.now().date() - datetime.timedelta(days=365*17)
            )
            customer.full_clean()

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67'
        )
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            price=Decimal('29.99'),
            quantity=10,
            publisher=self.publisher
        )
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address='Test Address'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=self.book.price,
            quantity=2
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.id}')

    def test_order_total_cost(self):
        self.assertEqual(self.order.get_total_cost(), Decimal('59.98'))

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67'
        )
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            price=Decimal('29.99'),
            quantity=10,
            publisher=self.publisher
        )

    def test_book_list_view(self):
        response = self.client.get(reverse('books:book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_list.html')
        self.assertContains(response, 'Test Book')

    def test_book_detail_view(self):
        response = self.client.get(
            reverse('books:book_detail', args=[self.book.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_detail.html')
        self.assertContains(response, 'Test Book')

    def test_cart_operations(self):
        # Тест добавления в корзину
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('books:cart_add', args=[self.book.id]),
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)

        # Тест просмотра корзины
        response = self.client.get(reverse('books:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/cart_detail.html')

    def test_order_creation(self):
        self.client.login(username='testuser', password='testpass123')
        # Добавляем книгу в корзину
        self.client.post(
            reverse('books:cart_add', args=[self.book.id]),
            {'quantity': 1}
        )
        # Создаем заказ
        response = self.client.post(
            reverse('books:order_create'),
            {'shipping_address': 'Test Address'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

    def test_statistics_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('books:statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/statistics.html')
