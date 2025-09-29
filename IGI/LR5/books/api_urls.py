"""
API URLs for the books app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import api_views

app_name = 'books_api'

urlpatterns = [
    # Books
    path('books/', api_views.BookListAPIView.as_view(), name='book-list'),
    path('books/<int:pk>/', api_views.BookDetailAPIView.as_view(), name='book-detail'),
    
    # Authors, Genres, Publishers
    path('authors/', api_views.AuthorListAPIView.as_view(), name='author-list'),
    path('genres/', api_views.GenreListAPIView.as_view(), name='genre-list'),
    path('publishers/', api_views.PublisherListAPIView.as_view(), name='publisher-list'),
    
    # Cart
    path('cart/', api_views.CartAPIView.as_view(), name='cart'),
    path('cart/add/', api_views.add_to_cart_api, name='cart-add'),
    path('cart/remove/<int:book_id>/', api_views.remove_from_cart_api, name='cart-remove'),
    path('cart/update/<int:book_id>/', api_views.update_cart_item_api, name='cart-update'),
    
    # Orders
    path('orders/', api_views.OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', api_views.OrderDetailAPIView.as_view(), name='order-detail'),
    
    # Reviews
    path('reviews/', api_views.ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path('books/<int:book_id>/reviews/', api_views.ReviewListCreateAPIView.as_view(), name='book-review-list-create'),
    
    # Customer Reviews
    path('customer-reviews/', api_views.CustomerReviewListCreateAPIView.as_view(), name='customer-review-list-create'),
    
    # Content
    path('banners/', api_views.BannerListAPIView.as_view(), name='banner-list'),
    path('partners/', api_views.PartnerListAPIView.as_view(), name='partner-list'),
    path('company-history/', api_views.CompanyHistoryListAPIView.as_view(), name='company-history-list'),
    path('faqs/', api_views.FAQListAPIView.as_view(), name='faq-list'),
    path('articles/', api_views.ArticleListAPIView.as_view(), name='article-list'),
    path('articles/<int:pk>/', api_views.ArticleDetailAPIView.as_view(), name='article-detail'),
    path('terms/', api_views.TermListAPIView.as_view(), name='term-list'),
    path('employees/', api_views.EmployeeListAPIView.as_view(), name='employee-list'),
    
    # Search and Statistics
    path('search/', api_views.search_api, name='search'),
    path('statistics/', api_views.statistics_api, name='statistics'),
    
    # Customer
    path('customer/', api_views.CustomerAPIView.as_view(), name='customer'),
]