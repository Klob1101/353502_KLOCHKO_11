"""
Comprehensive tests for the books app services.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import datetime

from books.models import (
    Book, Author, Genre, Publisher, Customer, Order, OrderItem, 
    Review, Cart, CartItem, PromoCode, Banner, Partner,
    CompanyHistory, CustomerReview, FAQ
)
from books.services import (
    CartService, OrderService, StatisticsService, 
    ReviewService, SearchService
)

User = get_user_model()


class CartServiceTest(TestCase):
    """Test cart service functionality"""
    
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
        
        self.author = Author.objects.create(name='Test Author')
        self.genre = Genre.objects.create(name='Test Genre')
        self.publisher = Publisher.objects.create(name='Test Publisher')
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('29.99'),
            quantity=10,
            description='Test description',
            publisher=self.publisher
        )
        self.book.authors.add(self.author)
        self.book.genres.add(self.genre)
    
    def test_get_or_create_cart(self):
        """Test cart creation for user"""
        cart = CartService.get_or_create_cart(self.user)
        self.assertIsInstance(cart, Cart)
        self.assertEqual(cart.user, self.user)
        
        # Test getting existing cart
        cart2 = CartService.get_or_create_cart(self.user)
        self.assertEqual(cart.id, cart2.id)
    
    def test_add_to_cart_success(self):
        """Test adding book to cart successfully"""
        result = CartService.add_to_cart(self.user, self.book, 2)
        
        self.assertTrue(result['success'])
        self.assertIn('added', result['message'].lower())
        
        cart = CartService.get_or_create_cart(self.user)
        cart_item = CartItem.objects.get(cart=cart, book=self.book)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_add_to_cart_out_of_stock(self):
        """Test adding out of stock book to cart"""
        self.book.quantity = 0
        self.book.save()
        
        result = CartService.add_to_cart(self.user, self.book, 1)
        
        self.assertFalse(result['success'])
        self.assertIn('stock', result['message'].lower())
    
    def test_add_to_cart_insufficient_quantity(self):
        """Test adding more books than available"""
        CartService.add_to_cart(self.user, self.book, 5)  # First add
        result = CartService.add_to_cart(self.user, self.book, 10)  # Add more than available
        
        self.assertFalse(result['success'])
        self.assertIn('stock', result['message'].lower())
    
    def test_remove_from_cart(self):
        """Test removing book from cart"""
        CartService.add_to_cart(self.user, self.book, 1)
        result = CartService.remove_from_cart(self.user, self.book)
        
        self.assertTrue(result['success'])
        
        cart = CartService.get_or_create_cart(self.user)
        self.assertFalse(CartItem.objects.filter(cart=cart, book=self.book).exists())
    
    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        CartService.add_to_cart(self.user, self.book, 1)
        result = CartService.update_cart_item(self.user, self.book, 3)
        
        self.assertTrue(result['success'])
        
        cart = CartService.get_or_create_cart(self.user)
        cart_item = CartItem.objects.get(cart=cart, book=self.book)
        self.assertEqual(cart_item.quantity, 3)
    
    def test_clear_cart(self):
        """Test clearing cart"""
        CartService.add_to_cart(self.user, self.book, 1)
        CartService.clear_cart(self.user)
        
        cart = CartService.get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 0)


class OrderServiceTest(TestCase):
    """Test order service functionality"""
    
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
        
        self.author = Author.objects.create(name='Test Author')
        self.publisher = Publisher.objects.create(name='Test Publisher')
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('29.99'),
            quantity=10,
            publisher=self.publisher
        )
        
        self.promocode = PromoCode.objects.create(
            code='TEST10',
            discount_percent=10,
            active=True,
            valid_from=timezone.now().date() - datetime.timedelta(days=1),
            valid_to=timezone.now().date() + datetime.timedelta(days=30)
        )
    
    def test_create_order_success(self):
        """Test successful order creation"""
        CartService.add_to_cart(self.user, self.book, 2)
        
        result = OrderService.create_order(
            customer=self.customer,
            shipping_address='Test Shipping Address'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('order', result)
        
        order = result['order']
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.items.count(), 1)
        
        order_item = order.items.first()
        self.assertEqual(order_item.book, self.book)
        self.assertEqual(order_item.quantity, 2)
        
        # Check stock was updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.quantity, 8)
        
        # Check cart was cleared
        cart = CartService.get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 0)
    
    def test_create_order_empty_cart(self):
        """Test order creation with empty cart"""
        result = OrderService.create_order(
            customer=self.customer,
            shipping_address='Test Address'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('empty', result['message'].lower())
    
    def test_create_order_insufficient_stock(self):
        """Test order creation with insufficient stock"""
        self.book.quantity = 1
        self.book.save()
        
        CartService.add_to_cart(self.user, self.book, 5)
        
        result = OrderService.create_order(
            customer=self.customer,
            shipping_address='Test Address'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('stock', result['message'].lower())
    
    def test_apply_valid_promocode(self):
        """Test applying valid promocode"""
        order = Order.objects.create(
            customer=self.customer,
            shipping_address='Test Address'
        )
        
        result = OrderService.apply_promocode(order, 'TEST10')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['discount'], 10)
        
        order.refresh_from_db()
        self.assertEqual(order.promocode, self.promocode)
    
    def test_apply_invalid_promocode(self):
        """Test applying invalid promocode"""
        order = Order.objects.create(
            customer=self.customer,
            shipping_address='Test Address'
        )
        
        result = OrderService.apply_promocode(order, 'INVALID')
        
        self.assertFalse(result['success'])
        self.assertIn('invalid', result['message'].lower())


class ReviewServiceTest(TestCase):
    """Test review service functionality"""
    
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
    
    def test_add_review_success(self):
        """Test adding review successfully"""
        result = ReviewService.add_review(
            customer=self.customer,
            book=self.book,
            rating=5,
            comment='Great book!'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('review', result)
        
        review = result['review']
        self.assertEqual(review.customer, self.customer)
        self.assertEqual(review.book, self.book)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great book!')
    
    def test_add_duplicate_review(self):
        """Test adding duplicate review"""
        ReviewService.add_review(self.customer, self.book, 5, 'First review')
        
        result = ReviewService.add_review(
            self.customer, self.book, 4, 'Second review'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('already', result['message'].lower())
    
    def test_get_book_reviews(self):
        """Test getting book reviews"""
        # Create approved and unapproved reviews
        review1 = Review.objects.create(
            customer=self.customer,
            book=self.book,
            rating=5,
            comment='Approved review',
            is_approved=True
        )
        
        user2 = User.objects.create_user(username='user2', password='pass')
        customer2 = Customer.objects.create(
            user=user2,
            phone='+375 (29) 987-65-43',
            address='Address 2',
            birth_date=datetime.date(1985, 1, 1)
        )
        
        review2 = Review.objects.create(
            customer=customer2,
            book=self.book,
            rating=3,
            comment='Unapproved review',
            is_approved=False
        )
        
        # Test getting only approved reviews
        approved_reviews = ReviewService.get_book_reviews(self.book, approved_only=True)
        self.assertEqual(len(approved_reviews), 1)
        self.assertEqual(approved_reviews[0], review1)
        
        # Test getting all reviews
        all_reviews = ReviewService.get_book_reviews(self.book, approved_only=False)
        self.assertEqual(len(all_reviews), 2)
    
    def test_approve_review(self):
        """Test approving review"""
        review = Review.objects.create(
            customer=self.customer,
            book=self.book,
            rating=4,
            comment='Test review',
            is_approved=False
        )
        
        result = ReviewService.approve_review(review.id)
        
        self.assertTrue(result['success'])
        
        review.refresh_from_db()
        self.assertTrue(review.is_approved)


class SearchServiceTest(TestCase):
    """Test search service functionality"""
    
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
    
    def test_search_by_title(self):
        """Test searching books by title"""
        books = SearchService.search_books('Python')
        
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], self.book1)
    
    def test_search_by_author(self):
        """Test searching books by author"""
        books = SearchService.search_books('Jane')
        
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], self.book2)
    
    def test_filter_by_genre(self):
        """Test filtering books by genre"""
        books = SearchService.search_books('', genre_ids=[self.genre1.id])
        
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], self.book2)
    
    def test_filter_by_price(self):
        """Test filtering books by price range"""
        books = SearchService.search_books(
            '', 
            min_price=Decimal('30.00'), 
            max_price=Decimal('50.00')
        )
        
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], self.book1)
    
    def test_sort_by_price(self):
        """Test sorting books by price"""
        books = SearchService.search_books('', sort_by='price')
        
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0], self.book2)  # Cheaper book first
        self.assertEqual(books[1], self.book1)


class StatisticsServiceTest(TransactionTestCase):
    """Test statistics service functionality"""
    
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
        
        self.book1 = Book.objects.create(
            title='Book 1',
            isbn='1111111111111',
            price=Decimal('20.00'),
            quantity=100,
            publisher=self.publisher
        )
        
        self.book2 = Book.objects.create(
            title='Book 2',
            isbn='2222222222222',
            price=Decimal('30.00'),
            quantity=100,
            publisher=self.publisher
        )
        
        # Create orders with items
        self.order1 = Order.objects.create(
            customer=self.customer,
            shipping_address='Address 1'
        )
        
        OrderItem.objects.create(
            order=self.order1,
            book=self.book1,
            quantity=2,
            price=self.book1.price
        )
        
        OrderItem.objects.create(
            order=self.order1,
            book=self.book2,
            quantity=1,
            price=self.book2.price
        )
    
    def test_calculate_sales_statistics(self):
        """Test calculating sales statistics"""
        stats = StatisticsService.calculate_sales_statistics()
        
        self.assertEqual(stats['total_orders'], 1)
        self.assertEqual(stats['total_revenue'], Decimal('70.00'))  # 2*20 + 1*30
        self.assertEqual(stats['avg_order_value'], Decimal('70.00'))
        self.assertEqual(stats['customers_with_orders'], 1)
        
        # Check top books
        top_books = list(stats['top_books'])
        self.assertEqual(len(top_books), 2)
        self.assertEqual(top_books[0], self.book1)  # Sold 2 copies
        self.assertEqual(top_books[0].total_sold, 2)
    
    def test_get_monthly_sales(self):
        """Test getting monthly sales data"""
        current_year = timezone.now().year
        monthly_sales = StatisticsService.get_monthly_sales(current_year)
        
        self.assertEqual(len(monthly_sales), 12)
        
        # Current month should have sales
        current_month = timezone.now().month
        self.assertEqual(monthly_sales[current_month], Decimal('70.00'))
        
        # Other months should be 0
        for month, sales in monthly_sales.items():
            if month != current_month:
                self.assertEqual(sales, Decimal('0.00'))


class ModelTest(TestCase):
    """Test new models"""
    
    def test_partner_model(self):
        """Test Partner model"""
        partner = Partner.objects.create(
            name='Partner Company',
            website='https://partner.com',
            description='A great partner'
        )
        
        self.assertEqual(str(partner), 'Partner Company')
        self.assertTrue(partner.is_active)
    
    def test_banner_model(self):
        """Test Banner model"""
        banner = Banner.objects.create(
            title='Test Banner',
            description='Banner description'
        )
        
        self.assertEqual(str(banner), 'Test Banner')
        self.assertTrue(banner.is_active)
        self.assertEqual(banner.order, 0)
    
    def test_company_history_model(self):
        """Test CompanyHistory model"""
        history = CompanyHistory.objects.create(
            year=2020,
            title='Company Founded',
            description='The company was founded'
        )
        
        self.assertEqual(str(history), '2020 - Company Founded')
    
    def test_customer_review_model(self):
        """Test CustomerReview model"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        customer = Customer.objects.create(
            user=user,
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=datetime.date(1990, 1, 1)
        )
        
        review = CustomerReview.objects.create(
            customer=customer,
            rating=5,
            title='Great Service',
            text='Excellent customer service!'
        )
        
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)
        self.assertIn('5★', str(review))
    
    def test_faq_model(self):
        """Test FAQ model"""
        faq = FAQ.objects.create(
            question='How to place an order?',
            answer='You can place an order by...',
            category='Orders'
        )
        
        self.assertEqual(str(faq), 'How to place an order?')
        self.assertTrue(faq.is_published)
    
    def test_cart_model(self):
        """Test Cart and CartItem models"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        cart = Cart.objects.create(user=user)
        self.assertEqual(str(cart), 'Cart for testuser')
        
        publisher = Publisher.objects.create(name='Test Publisher')
        book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            price=Decimal('25.00'),
            quantity=10,
            publisher=publisher
        )
        
        cart_item = CartItem.objects.create(
            cart=cart,
            book=book,
            quantity=2
        )
        
        self.assertEqual(str(cart_item), '2x Test Book')
        self.assertEqual(cart_item.get_cost(), Decimal('50.00'))
        self.assertEqual(cart.get_total_cost(), Decimal('50.00'))
        self.assertEqual(cart.get_total_items(), 2)