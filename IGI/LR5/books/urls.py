from django.urls import path, re_path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/review/', views.add_review, name='add_review'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:book_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:book_id>/', views.cart_remove, name='cart_remove'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('reviews/moderate/', views.moderate_reviews, name='moderate_reviews'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancies/create/', views.vacancy_create, name='vacancy_create'),
    path('vacancies/<int:pk>/edit/', views.vacancy_update, name='vacancy_update'),
    re_path(r'^vacancies/(?P<pk>\d+)/delete/$', views.vacancy_delete, name='vacancy_delete'),
    path('about/', views.company_info, name='company_info'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('terms/', views.terms_list, name='terms_list'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('promocodes/', views.promocode_list, name='promocode_list'),
    path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
] 