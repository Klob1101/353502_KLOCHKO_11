"""
API serializers for the books app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Book, Author, Genre, Publisher, Order, OrderItem, 
    Review, Customer, Cart, CartItem, Banner, Partner,
    CompanyHistory, CustomerReview, FAQ, Article, Term, Employee
)

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model"""
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'photo']


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model"""
    
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model"""
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'address', 'website']


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for Book list view"""
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'genres', 'publisher', 'isbn',
            'price', 'quantity', 'cover', 'avg_rating', 'created_at'
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer for Book detail view"""
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'genres', 'publisher', 'isbn',
            'description', 'price', 'quantity', 'cover', 'avg_rating',
            'reviews_count', 'created_at', 'updated_at'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'email', 'phone', 'address', 
            'birth_date', 'timezone', 'created_at'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    customer = CustomerSerializer(read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'customer', 'book', 'book_title', 'rating', 
            'comment', 'created_at', 'is_approved'
        ]
        read_only_fields = ['customer', 'is_approved']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['book', 'rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model"""
    book = BookListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'book', 'book_id', 'quantity', 'total_cost', 'created_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_cost'] = instance.get_cost()
        return representation


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    items = CartItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_cost', 'total_items', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_cost'] = instance.get_total_cost()
        representation['total_items'] = instance.get_total_items()
        return representation


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    book = BookListSerializer(read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'price', 'total_cost']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_cost'] = instance.get_cost()
        return representation


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'items', 'shipping_address', 'total_cost',
            'created_at', 'updated_at', 'delivery_date', 'pickup_point', 'promocode'
        ]
        read_only_fields = ['customer']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_cost'] = instance.get_total_cost()
        return representation


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    promocode_str = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'delivery_date', 'pickup_point', 'promocode_str']


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for Banner model"""
    
    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'image', 'link', 'is_active', 'order']


class PartnerSerializer(serializers.ModelSerializer):
    """Serializer for Partner model"""
    
    class Meta:
        model = Partner
        fields = ['id', 'name', 'logo', 'website', 'description', 'is_active', 'created_at']


class CompanyHistorySerializer(serializers.ModelSerializer):
    """Serializer for CompanyHistory model"""
    
    class Meta:
        model = CompanyHistory
        fields = ['id', 'year', 'title', 'description', 'image']


class CustomerReviewSerializer(serializers.ModelSerializer):
    """Serializer for CustomerReview model"""
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = CustomerReview
        fields = ['id', 'customer', 'rating', 'title', 'text', 'is_approved', 'created_at']
        read_only_fields = ['customer', 'is_approved']


class CustomerReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customer reviews"""
    
    class Meta:
        model = CustomerReview
        fields = ['rating', 'title', 'text']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model"""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'is_published', 'created_at', 'updated_at']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'content', 'image', 'published_at']


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for Article list view"""
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'image', 'published_at']


class TermSerializer(serializers.ModelSerializer):
    """Serializer for Term model"""
    
    class Meta:
        model = Term
        fields = ['id', 'term', 'definition', 'added_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    
    class Meta:
        model = Employee
        fields = ['id', 'name', 'photo', 'position', 'description', 'phone', 'email']


class SearchResultSerializer(serializers.Serializer):
    """Serializer for search results"""
    books = BookListSerializer(many=True, read_only=True)
    total_count = serializers.IntegerField(read_only=True)
    page = serializers.IntegerField(read_only=True)
    pages = serializers.IntegerField(read_only=True)