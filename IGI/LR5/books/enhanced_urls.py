"""
Enhanced URL patterns using the enhanced views with HTML5 semantic templates
"""
from django.urls import path, include
from . import enhanced_views

app_name = 'books_enhanced'

urlpatterns = [
    # Enhanced Home page with semantic HTML5
    path('', enhanced_views.HomeView.as_view(), name='home'),
    
    # Enhanced Book pages
    path('books/', enhanced_views.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', enhanced_views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:pk>/review/', enhanced_views.AddReviewView.as_view(), name='add_review'),
    
    # Enhanced Cart and Order pages
    path('cart/', enhanced_views.CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/<int:book_id>/', enhanced_views.CartAddView.as_view(), name='cart_add'),
    path('cart/remove/<int:book_id>/', enhanced_views.CartRemoveView.as_view(), name='cart_remove'),
    path('checkout/', enhanced_views.CheckoutView.as_view(), name='checkout'),
    path('order/create/', enhanced_views.OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/', enhanced_views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/', enhanced_views.OrderListView.as_view(), name='order_list'),
    
    # Enhanced Company and Information pages
    path('about/', enhanced_views.CompanyInfoView.as_view(), name='company_info'),
    path('news/', enhanced_views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', enhanced_views.NewsDetailView.as_view(), name='news_detail'),
    path('contacts/', enhanced_views.ContactView.as_view(), name='contacts'),
    path('privacy/', enhanced_views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', enhanced_views.TermsListView.as_view(), name='terms_list'),
    
    # Enhanced HR and Promotional pages
    path('vacancies/', enhanced_views.VacancyListView.as_view(), name='vacancy_list'),
    path('promocodes/', enhanced_views.PromoCodeListView.as_view(), name='promocode_list'),
    path('reviews/', enhanced_views.ReviewsView.as_view(), name='reviews'),
    path('faq/', enhanced_views.FAQView.as_view(), name='faq'),
    
    # Payment page
    path('payment/', enhanced_views.PaymentView.as_view(), name='payment'),
    
    # API endpoints (unchanged)
    path('api/', include('books.api_urls')),
]