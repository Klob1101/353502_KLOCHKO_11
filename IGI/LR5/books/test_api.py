"""
Comprehensive API tests for the books app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
import datetime
import json

from books.models import (
    Book, Author, Genre, Publisher, Customer, Order, OrderItem,
    Review, Cart, CartItem, PromoCode, Banner, Partner,
    CompanyHistory, CustomerReview, FAQ, Article, Term, Employee
)
from books.services import CartService

User = get_user_model()


class BookAPITest(APITestCase):
    """Test Book API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.author = Author.objects.create(name='Test Author', bio='Test bio')
        self.genre = Genre.objects.create(name='Test Genre', description='Test description')
        self.publisher = Publisher.objects.create(name='Test Publisher', address='Test address')
        
        self.book1 = Book.objects.create(
            title='Test Book 1',
            isbn='1234567890123',
            price=Decimal('29.99'),
            quantity=10,
            description='Test description 1',
            publisher=self.publisher
        )
        self.book1.authors.add(self.author)
        self.book1.genres.add(self.genre)
        
        self.book2 = Book.objects.create(
            title='Another Book',
            isbn='1234567890124',
            price=Decimal('39.99'),
            quantity=5,
            description='Test description 2',
            publisher=self.publisher
        )
        self.book2.authors.add(self.author)
        self.book2.genres.add(self.genre)
    
    def test_book_list_api(self):
        """Test book list API"""
        url = reverse('books_api:book-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Check book data structure
        book_data = response.data['results'][0]
        self.assertIn('id', book_data)
        self.assertIn('title', book_data)
        self.assertIn('authors', book_data)
        self.assertIn('genres', book_data)
        self.assertIn('publisher', book_data)
        self.assertIn('price', book_data)
        self.assertIn('avg_rating', book_data)
    
    def test_book_detail_api(self):
        """Test book detail API"""
        url = reverse('books_api:book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book 1')
        self.assertEqual(response.data['isbn'], '1234567890123')
        self.assertIn('description', response.data)
        self.assertIn('reviews_count', response.data)
    
    def test_book_search_api(self):
        """Test book search functionality"""
        url = reverse('books_api:book-list')
        
        # Search by title
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search by author
        response = self.client.get(url, {'search': 'Test Author'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_book_filter_by_price(self):
        """Test filtering books by price"""
        url = reverse('books_api:book-list')
        
        # Filter by min price
        response = self.client.get(url, {'min_price': '35.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Another Book')
        
        # Filter by max price
        response = self.client.get(url, {'max_price': '30.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Book 1')
    
    def test_book_sort(self):
        """Test sorting books"""
        url = reverse('books_api:book-list')
        
        # Sort by price ascending
        response = self.client.get(url, {'sort_by': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Test Book 1')
        self.assertEqual(results[1]['title'], 'Another Book')
        
        # Sort by price descending
        response = self.client.get(url, {'sort_by': '-price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Another Book')
        self.assertEqual(results[1]['title'], 'Test Book 1')


class CartAPITest(APITestCase):
    """Test Cart API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=datetime.date(1990, 1, 1)
        )
        
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('29.99'),
            quantity=10,
            publisher=self.publisher
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_cart_api(self):
        """Test getting cart via API"""
        url = reverse('books_api:cart')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total_cost', response.data)
        self.assertIn('total_items', response.data)
        self.assertEqual(len(response.data['items']), 0)
    
    def test_add_to_cart_api(self):
        """Test adding item to cart via API"""
        url = reverse('books_api:cart-add')
        data = {
            'book_id': self.book.id,
            'quantity': 2
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('cart', response.data)
        
        # Check cart contents
        cart_data = response.data['cart']
        self.assertEqual(len(cart_data['items']), 1)
        self.assertEqual(cart_data['items'][0]['quantity'], 2)
        self.assertEqual(cart_data['total_items'], 2)
    
    def test_add_invalid_book_to_cart(self):
        """Test adding non-existent book to cart"""
        url = reverse('books_api:cart-add')
        data = {
            'book_id': 999,
            'quantity': 1
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_add_excessive_quantity_to_cart(self):
        """Test adding more items than available"""
        url = reverse('books_api:cart-add')
        data = {
            'book_id': self.book.id,
            'quantity': 15  # More than available (10)
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_remove_from_cart_api(self):
        """Test removing item from cart via API"""
        # First add item to cart
        CartService.add_to_cart(self.user, self.book, 1)
        
        url = reverse('books_api:cart-remove', kwargs={'book_id': self.book.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check cart is empty
        cart_data = response.data['cart']
        self.assertEqual(len(cart_data['items']), 0)
    
    def test_update_cart_item_api(self):
        """Test updating cart item quantity via API"""
        # First add item to cart
        CartService.add_to_cart(self.user, self.book, 2)
        
        url = reverse('books_api:cart-update', kwargs={'book_id': self.book.id})
        data = {'quantity': 5}
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check updated quantity
        cart_data = response.data['cart']
        self.assertEqual(cart_data['items'][0]['quantity'], 5)
    
    def test_cart_api_requires_authentication(self):
        """Test that cart APIs require authentication"""
        self.client.force_authenticate(user=None)
        
        # Test get cart
        url = reverse('books_api:cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test add to cart
        url = reverse('books_api:cart-add')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderAPITest(APITestCase):
    """Test Order API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=datetime.date(1990, 1, 1)
        )
        
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('29.99'),
            quantity=10,
            publisher=self.publisher
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_order_api(self):
        """Test creating order via API"""
        # Add item to cart first
        CartService.add_to_cart(self.user, self.book, 2)
        
        url = reverse('books_api:order-list-create')
        data = {
            'shipping_address': 'Test Shipping Address'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['shipping_address'], 'Test Shipping Address')
        self.assertEqual(len(response.data['items']), 1)
        
        # Check that order was created in database
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.items.count(), 1)
    
    def test_create_order_with_empty_cart(self):
        """Test creating order with empty cart"""
        url = reverse('books_api:order-list-create')
        data = {
            'shipping_address': 'Test Address'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_order_list_api(self):
        """Test getting order list via API"""
        # Create test order
        order = Order.objects.create(
            customer=self.customer,
            shipping_address='Test Address'
        )
        OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=1,
            price=self.book.price
        )
        
        url = reverse('books_api:order-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        order_data = response.data['results'][0]
        self.assertEqual(order_data['shipping_address'], 'Test Address')
        self.assertEqual(len(order_data['items']), 1)
    
    def test_get_order_detail_api(self):
        """Test getting order detail via API"""
        # Create test order
        order = Order.objects.create(
            customer=self.customer,
            shipping_address='Test Address'
        )
        OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=2,
            price=self.book.price
        )
        
        url = reverse('books_api:order-detail', kwargs={'pk': order.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 2)


class ReviewAPITest(APITestCase):
    """Test Review API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=datetime.date(1990, 1, 1)
        )
        
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('29.99'),
            quantity=10,
            publisher=self.publisher
        )
        
        self.client = APIClient()
    
    def test_get_reviews_api(self):
        """Test getting reviews via API"""
        # Create approved review
        Review.objects.create(
            customer=self.customer,
            book=self.book,
            rating=5,
            comment='Great book!',
            is_approved=True
        )
        
        # Create unapproved review for same book but different customer
        user2 = User.objects.create_user(username='user2', password='pass')
        customer2 = Customer.objects.create(
            user=user2,
            phone='+375 (29) 987-65-43',
            address='Address 2',
            birth_date=datetime.date(1985, 1, 1)
        )
        
        # Create another book for second review to avoid constraint violation
        book2 = Book.objects.create(
            title='Another Book',
            isbn='1234567890124',
            price=Decimal('19.99'),
            quantity=5,
            publisher=self.publisher
        )
        
        # Create unapproved review for different book
        Review.objects.create(
            customer=customer2,
            book=book2,
            rating=3,
            comment='Unapproved review',
            is_approved=False
        )
        
        url = reverse('books_api:review-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only show approved reviews
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['comment'], 'Great book!')
    
    def test_create_review_api(self):
        """Test creating review via API"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('books_api:review-list-create')
        data = {
            'book': self.book.id,
            'rating': 5,
            'comment': 'Excellent book!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check review was created
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.customer, self.customer)
        self.assertEqual(review.book, self.book)
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)  # Should not be auto-approved
    
    def test_create_duplicate_review(self):
        """Test creating duplicate review"""
        self.client.force_authenticate(user=self.user)
        
        # Create first review
        Review.objects.create(
            customer=self.customer,
            book=self.book,
            rating=4,
            comment='First review'
        )
        
        url = reverse('books_api:review-list-create')
        data = {
            'book': self.book.id,
            'rating': 5,
            'comment': 'Second review'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_review_requires_authentication(self):
        """Test that creating reviews requires authentication"""
        url = reverse('books_api:review-list-create')
        data = {
            'book': self.book.id,
            'rating': 5,
            'comment': 'Test review'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchAPITest(APITestCase):
    """Test Search API functionality"""
    
    def setUp(self):
        self.author1 = Author.objects.create(name='John Doe')
        self.author2 = Author.objects.create(name='Jane Smith')
        self.genre1 = Genre.objects.create(name='Fiction')
        self.genre2 = Genre.objects.create(name='Science')
        self.publisher = Publisher.objects.create(name='Test Publisher')
        
        self.book1 = Book.objects.create(
            title='Python Programming',
            isbn='1111111111111',
            price=Decimal('39.99'),
            quantity=5,
            description='Learn Python programming',
            publisher=self.publisher
        )
        self.book1.authors.add(self.author1)
        self.book1.genres.add(self.genre2)
        
        self.book2 = Book.objects.create(
            title='Fiction Novel',
            isbn='2222222222222',
            price=Decimal('19.99'),
            quantity=3,
            description='A great fiction story',
            publisher=self.publisher
        )
        self.book2.authors.add(self.author2)
        self.book2.genres.add(self.genre1)
    
    def test_search_api(self):
        """Test comprehensive search API"""
        url = reverse('books_api:search')
        
        # Search by title
        response = self.client.get(url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Programming')
        
        # Search by author
        response = self.client.get(url, {'q': 'Jane'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Fiction Novel')
        
        # Filter by genre
        response = self.client.get(url, {'genres': str(self.genre1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Fiction Novel')
        
        # Filter by price range
        response = self.client.get(url, {'min_price': '30.00', 'max_price': '50.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Programming')


class StatisticsAPITest(APITestCase):
    """Test Statistics API functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=datetime.date(1990, 1, 1)
        )
        
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('25.00'),
            quantity=100,
            publisher=self.publisher
        )
        
        # Create test order
        self.order = Order.objects.create(
            customer=self.customer,
            shipping_address='Test Address'
        )
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            quantity=3,
            price=self.book.price
        )
    
    def test_statistics_api(self):
        """Test statistics API endpoint"""
        url = reverse('books_api:statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('sales_statistics', response.data)
        self.assertIn('monthly_sales', response.data)
        self.assertIn('top_books', response.data)
        
        # Check sales statistics
        sales_stats = response.data['sales_statistics']
        self.assertEqual(int(sales_stats['total_orders']), 1)
        self.assertEqual(Decimal(sales_stats['total_revenue']), Decimal('75.00'))  # 3 * 25.00
        
        # Check monthly sales structure
        monthly_sales = response.data['monthly_sales']
        self.assertIn('year', monthly_sales)
        self.assertIn('data', monthly_sales)
        self.assertEqual(len(monthly_sales['data']), 12)  # 12 months
        
        # Check top books
        top_books = response.data['top_books']
        self.assertEqual(len(top_books), 1)
        self.assertEqual(top_books[0]['title'], 'Test Book')