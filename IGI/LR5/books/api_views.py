"""
API views for the books app.
"""
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal

from .models import (
    Book, Author, Genre, Publisher, Order, OrderItem, 
    Review, Customer, Cart, CartItem, Banner, Partner,
    CompanyHistory, CustomerReview, FAQ, Article, Term, Employee
)
from .serializers import (
    BookListSerializer, BookDetailSerializer, AuthorSerializer,
    GenreSerializer, PublisherSerializer, OrderSerializer,
    OrderCreateSerializer, ReviewSerializer, ReviewCreateSerializer,
    CartSerializer, CartItemSerializer, CustomerSerializer,
    BannerSerializer, PartnerSerializer, CompanyHistorySerializer,
    CustomerReviewSerializer, CustomerReviewCreateSerializer,
    FAQSerializer, ArticleSerializer, ArticleListSerializer,
    TermSerializer, EmployeeSerializer, SearchResultSerializer
)
from rest_framework import serializers
from .services import CartService, OrderService, ReviewService, SearchService


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookFilter:
    """Custom filter for books"""
    
    @staticmethod
    def filter_books(queryset, search=None, genre_ids=None, min_price=None, max_price=None, sort_by=None):
        """Apply filters to book queryset"""
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(authors__name__icontains=search) |
                Q(description__icontains=search) |
                Q(isbn__icontains=search)
            ).distinct()
        
        if genre_ids:
            genre_list = [int(g) for g in genre_ids.split(',') if g.isdigit()]
            if genre_list:
                queryset = queryset.filter(genres__id__in=genre_list)
        
        if min_price is not None:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except (ValueError, TypeError):
                pass
        
        if max_price is not None:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except (ValueError, TypeError):
                pass
        
        # Apply sorting
        valid_sorts = ['title', '-title', 'price', '-price', 'created_at', '-created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('title')
        
        return queryset


class BookListAPIView(generics.ListAPIView):
    """API view for listing books"""
    serializer_class = BookListSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Book.objects.select_related('publisher').prefetch_related(
            'authors', 'genres', 'reviews'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        # Apply filters
        search = self.request.query_params.get('search')
        genre_ids = self.request.query_params.get('genres')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        sort_by = self.request.query_params.get('sort_by', 'title')
        
        return BookFilter.filter_books(
            queryset, search, genre_ids, min_price, max_price, sort_by
        )


class BookDetailAPIView(generics.RetrieveAPIView):
    """API view for book details"""
    queryset = Book.objects.select_related('publisher').prefetch_related(
        'authors', 'genres', 'reviews'
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
    )
    serializer_class = BookDetailSerializer


class AuthorListAPIView(generics.ListAPIView):
    """API view for listing authors"""
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'bio']


class GenreListAPIView(generics.ListAPIView):
    """API view for listing genres"""
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class PublisherListAPIView(generics.ListAPIView):
    """API view for listing publishers"""
    queryset = Publisher.objects.all().order_by('name')
    serializer_class = PublisherSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CartAPIView(generics.RetrieveAPIView):
    """API view for user's cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return CartService.get_or_create_cart(self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_api(request):
    """API endpoint for adding items to cart"""
    book_id = request.data.get('book_id')
    quantity = request.data.get('quantity', 1)
    
    if not book_id:
        return Response(
            {'error': 'book_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid quantity'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = CartService.add_to_cart(request.user, book, quantity)
    
    if result['success']:
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response({
            'message': result['message'],
            'cart': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': result['message']}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart_api(request, book_id):
    """API endpoint for removing items from cart"""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    result = CartService.remove_from_cart(request.user, book)
    
    if result['success']:
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response({
            'message': result['message'],
            'cart': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': result['message']}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item_api(request, book_id):
    """API endpoint for updating cart item quantity"""
    quantity = request.data.get('quantity')
    
    if quantity is None:
        return Response(
            {'error': 'quantity is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Book not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid quantity'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = CartService.update_cart_item(request.user, book, quantity)
    
    if result['success']:
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response({
            'message': result['message'],
            'cart': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': result['message']}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating orders"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        try:
            customer = self.request.user.customer
            return Order.objects.filter(customer=customer).select_related(
                'customer', 'customer__user'
            ).prefetch_related('items', 'items__book').order_by('-created_at')
        except Customer.DoesNotExist:
            return Order.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = OrderService.create_order(
            customer=customer,
            shipping_address=serializer.validated_data['shipping_address'],
            promocode=serializer.validated_data.get('promocode_str'),
            delivery_date=serializer.validated_data.get('delivery_date'),
            pickup_point_id=serializer.validated_data.get('pickup_point')
        )
        
        if result['success']:
            order_serializer = OrderSerializer(result['order'])
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result['message']}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderDetailAPIView(generics.RetrieveAPIView):
    """API view for order details"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            customer = self.request.user.customer
            return Order.objects.filter(customer=customer).select_related(
                'customer', 'customer__user'
            ).prefetch_related('items', 'items__book')
        except Customer.DoesNotExist:
            return Order.objects.none()


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating reviews"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        if book_id:
            return Review.objects.filter(
                book_id=book_id, 
                is_approved=True
            ).select_related('customer', 'customer__user').order_by('-created_at')
        return Review.objects.filter(is_approved=True).select_related(
            'customer', 'customer__user', 'book'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer profile not found")
        
        book = serializer.validated_data['book']
        
        # Check if customer already reviewed this book
        if Review.objects.filter(customer=customer, book=book).exists():
            raise serializers.ValidationError("You have already reviewed this book")
        
        serializer.save(customer=customer)


class CustomerReviewListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating customer reviews"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return CustomerReview.objects.filter(
            is_approved=True
        ).select_related('customer', 'customer__user').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomerReviewCreateSerializer
        return CustomerReviewSerializer
    
    def perform_create(self, serializer):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer profile not found")
        
        serializer.save(customer=customer)


class BannerListAPIView(generics.ListAPIView):
    """API view for listing banners"""
    queryset = Banner.objects.filter(is_active=True).order_by('order')
    serializer_class = BannerSerializer


class PartnerListAPIView(generics.ListAPIView):
    """API view for listing partners"""
    queryset = Partner.objects.filter(is_active=True).order_by('name')
    serializer_class = PartnerSerializer
    pagination_class = StandardResultsSetPagination


class CompanyHistoryListAPIView(generics.ListAPIView):
    """API view for listing company history"""
    queryset = CompanyHistory.objects.all().order_by('-year')
    serializer_class = CompanyHistorySerializer
    pagination_class = StandardResultsSetPagination


class FAQListAPIView(generics.ListAPIView):
    """API view for listing FAQs"""
    queryset = FAQ.objects.filter(is_published=True).order_by('category', 'question')
    serializer_class = FAQSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['question', 'answer']
    filterset_fields = ['category']


class ArticleListAPIView(generics.ListAPIView):
    """API view for listing articles"""
    queryset = Article.objects.all().order_by('-published_at')
    serializer_class = ArticleListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'summary', 'content']


class ArticleDetailAPIView(generics.RetrieveAPIView):
    """API view for article details"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class TermListAPIView(generics.ListAPIView):
    """API view for listing terms"""
    queryset = Term.objects.all().order_by('term')
    serializer_class = TermSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['term', 'definition']


class EmployeeListAPIView(generics.ListAPIView):
    """API view for listing employees"""
    queryset = Employee.objects.all().order_by('name')
    serializer_class = EmployeeSerializer
    pagination_class = StandardResultsSetPagination


@api_view(['GET'])
def search_api(request):
    """Comprehensive search API"""
    query = request.query_params.get('q', '')
    genre_ids = request.query_params.get('genres', '')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    sort_by = request.query_params.get('sort_by', 'title')
    
    # Convert genre_ids to list
    genre_list = [int(g) for g in genre_ids.split(',') if g.isdigit()] if genre_ids else []
    
    # Convert prices
    try:
        min_price = Decimal(min_price) if min_price else None
    except (ValueError, TypeError):
        min_price = None
    
    try:
        max_price = Decimal(max_price) if max_price else None
    except (ValueError, TypeError):
        max_price = None
    
    # Search books
    books = SearchService.search_books(
        query=query,
        genre_ids=genre_list,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )
    
    # Paginate results
    paginator = StandardResultsSetPagination()
    paginated_books = paginator.paginate_queryset(books, request)
    
    # Serialize results
    book_serializer = BookListSerializer(paginated_books, many=True)
    
    return paginator.get_paginated_response(book_serializer.data)


@api_view(['GET'])
def statistics_api(request):
    """API endpoint for statistics"""
    from .services import StatisticsService
    from django.utils import timezone
    
    # Get date range from query params
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    try:
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = None
    
    try:
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        end_date = None
    
    stats = StatisticsService.calculate_sales_statistics(start_date, end_date)
    
    # Get monthly sales for current year
    current_year = timezone.now().year
    monthly_sales = StatisticsService.get_monthly_sales(current_year)
    
    return Response({
        'sales_statistics': {
            'total_orders': stats['total_orders'],
            'total_revenue': str(stats['total_revenue']),
            'avg_order_value': str(stats['avg_order_value']),
            'customers_with_orders': stats['customers_with_orders'],
        },
        'monthly_sales': {
            'year': current_year,
            'data': {str(month): str(sales) for month, sales in monthly_sales.items()}
        },
        'top_books': BookListSerializer(stats['top_books'], many=True).data
    })


class CustomerAPIView(generics.RetrieveUpdateAPIView):
    """API view for customer profile"""
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Customer, user=self.request.user)