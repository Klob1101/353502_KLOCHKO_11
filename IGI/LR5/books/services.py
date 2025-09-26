"""
Business logic services for the books app.
"""
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging

from .models import (
    Book, Order, OrderItem, Review, Customer, 
    Cart, CartItem, SalesStatistics, PromoCode
)

User = get_user_model()
logger = logging.getLogger(__name__)


class CartService:
    """Service for cart operations"""
    
    @staticmethod
    def get_or_create_cart(user: User) -> Cart:
        """Get or create cart for user"""
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new cart for user {user.username}")
        return cart
    
    @staticmethod
    def add_to_cart(user: User, book: Book, quantity: int = 1) -> Dict[str, any]:
        """Add book to cart"""
        cart = CartService.get_or_create_cart(user)
        
        if not book.is_available():
            return {'success': False, 'message': 'Book is out of stock'}
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            book=book,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > book.quantity:
                return {'success': False, 'message': 'Not enough books in stock'}
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            if quantity > book.quantity:
                cart_item.delete()
                return {'success': False, 'message': 'Not enough books in stock'}
        
        logger.info(f"Added {quantity} of book {book.id} to cart for user {user.username}")
        return {'success': True, 'message': 'Book added to cart'}
    
    @staticmethod
    def remove_from_cart(user: User, book: Book) -> Dict[str, str]:
        """Remove book from cart"""
        cart = CartService.get_or_create_cart(user)
        try:
            cart_item = CartItem.objects.get(cart=cart, book=book)
            cart_item.delete()
            logger.info(f"Removed book {book.id} from cart for user {user.username}")
            return {'success': True, 'message': 'Book removed from cart'}
        except CartItem.DoesNotExist:
            return {'success': False, 'message': 'Book not in cart'}
    
    @staticmethod
    def update_cart_item(user: User, book: Book, quantity: int) -> Dict[str, str]:
        """Update cart item quantity"""
        cart = CartService.get_or_create_cart(user)
        try:
            cart_item = CartItem.objects.get(cart=cart, book=book)
            
            if quantity <= 0:
                return CartService.remove_from_cart(user, book)
            
            if quantity > book.quantity:
                return {'success': False, 'message': 'Not enough books in stock'}
            
            cart_item.quantity = quantity
            cart_item.save()
            
            logger.info(f"Updated cart item {book.id} quantity to {quantity} for user {user.username}")
            return {'success': True, 'message': 'Cart updated'}
        except CartItem.DoesNotExist:
            return {'success': False, 'message': 'Book not in cart'}
    
    @staticmethod
    def clear_cart(user: User) -> None:
        """Clear user's cart"""
        cart = CartService.get_or_create_cart(user)
        cart.items.all().delete()
        logger.info(f"Cleared cart for user {user.username}")


class OrderService:
    """Service for order operations"""
    
    @staticmethod
    def create_order(
        customer: Customer, 
        shipping_address: str,
        promocode: Optional[str] = None,
        delivery_date: Optional[str] = None,
        pickup_point_id: Optional[int] = None
    ) -> Dict[str, any]:
        """Create order from user's cart"""
        cart = CartService.get_or_create_cart(customer.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            return {'success': False, 'message': 'Cart is empty'}
        
        # Check stock availability
        for cart_item in cart_items:
            if cart_item.book.quantity < cart_item.quantity:
                return {
                    'success': False, 
                    'message': f'Not enough {cart_item.book.title} in stock'
                }
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            shipping_address=shipping_address
        )
        
        # Apply promocode if provided
        if promocode:
            promo_result = OrderService.apply_promocode(order, promocode)
            if not promo_result['success']:
                order.delete()
                return promo_result
        
        # Create order items and update stock
        total_cost = Decimal('0.00')
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                book=cart_item.book,
                quantity=cart_item.quantity,
                price=cart_item.book.price
            )
            
            # Update book stock
            cart_item.book.quantity -= cart_item.quantity
            cart_item.book.save()
            
            total_cost += order_item.get_cost()
        
        # Clear cart
        CartService.clear_cart(customer.user)
        
        logger.info(f"Created order {order.id} for customer {customer.id}")
        return {'success': True, 'order': order, 'total_cost': total_cost}
    
    @staticmethod
    def apply_promocode(order: Order, promocode: str) -> Dict[str, any]:
        """Apply promocode to order"""
        try:
            today = timezone.now().date()
            promo = PromoCode.objects.get(
                code=promocode,
                active=True,
                valid_from__lte=today,
                valid_to__gte=today
            )
            order.promocode = promo
            order.save()
            return {'success': True, 'discount': promo.discount_percent}
        except PromoCode.DoesNotExist:
            return {'success': False, 'message': 'Invalid or expired promocode'}


class StatisticsService:
    """Service for statistics calculations"""
    
    @staticmethod
    def calculate_sales_statistics(start_date=None, end_date=None) -> Dict[str, any]:
        """Calculate comprehensive sales statistics"""
        orders = Order.objects.all()
        
        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)
        
        # Basic statistics
        total_orders = orders.count()
        total_revenue = OrderItem.objects.filter(
            order__in=orders
        ).aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or Decimal('0.00')
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
        
        # Top selling books
        top_books = Book.objects.filter(
            orderitem__order__in=orders
        ).annotate(
            total_sold=Sum('orderitem__quantity'),
            total_revenue=Sum(F('orderitem__quantity') * F('orderitem__price'))
        ).order_by('-total_sold')[:10]
        
        # Customer statistics
        customers_with_orders = Customer.objects.filter(
            order__in=orders
        ).distinct().count()
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'top_books': top_books,
            'customers_with_orders': customers_with_orders,
        }
    
    @staticmethod
    def get_monthly_sales(year: int) -> Dict[int, Decimal]:
        """Get monthly sales for a given year"""
        from django.db.models.functions import Extract
        
        monthly_sales = OrderItem.objects.filter(
            order__created_at__year=year
        ).annotate(
            month=Extract('order__created_at', 'month')
        ).values('month').annotate(
            total=Sum(F('quantity') * F('price'))
        ).order_by('month')
        
        # Initialize all months with 0
        result = {i: Decimal('0.00') for i in range(1, 13)}
        
        for sale in monthly_sales:
            result[sale['month']] = sale['total'] or Decimal('0.00')
        
        return result


class ReviewService:
    """Service for review operations"""
    
    @staticmethod
    def add_review(customer: Customer, book: Book, rating: int, comment: str) -> Dict[str, any]:
        """Add a review for a book"""
        # Check if customer already reviewed this book
        if Review.objects.filter(customer=customer, book=book).exists():
            return {'success': False, 'message': 'You have already reviewed this book'}
        
        review = Review.objects.create(
            customer=customer,
            book=book,
            rating=rating,
            comment=comment
        )
        
        logger.info(f"Review created by customer {customer.id} for book {book.id}")
        return {'success': True, 'review': review}
    
    @staticmethod
    def get_book_reviews(book: Book, approved_only: bool = True) -> List[Review]:
        """Get reviews for a book"""
        reviews = book.reviews.all()
        if approved_only:
            reviews = reviews.filter(is_approved=True)
        return reviews.order_by('-created_at')
    
    @staticmethod
    def approve_review(review_id: int) -> Dict[str, any]:
        """Approve a review"""
        try:
            review = Review.objects.get(id=review_id, is_approved=False)
            review.is_approved = True
            review.save()
            logger.info(f"Review {review_id} approved")
            return {'success': True, 'message': 'Review approved'}
        except Review.DoesNotExist:
            return {'success': False, 'message': 'Review not found'}


class SearchService:
    """Service for search operations"""
    
    @staticmethod
    def search_books(
        query: str, 
        genre_ids: List[int] = None, 
        min_price: Decimal = None,
        max_price: Decimal = None,
        sort_by: str = 'title'
    ) -> List[Book]:
        """Search books with filters"""
        books = Book.objects.all()
        
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(authors__name__icontains=query) |
                Q(description__icontains=query) |
                Q(isbn__icontains=query)
            ).distinct()
        
        if genre_ids:
            books = books.filter(genres__id__in=genre_ids)
        
        if min_price is not None:
            books = books.filter(price__gte=min_price)
        
        if max_price is not None:
            books = books.filter(price__lte=max_price)
        
        # Sort books
        valid_sorts = ['title', '-title', 'price', '-price', 'created_at', '-created_at']
        if sort_by in valid_sorts:
            books = books.order_by(sort_by)
        else:
            books = books.order_by('title')
        
        return books.annotate(avg_rating=Avg('reviews__rating'))