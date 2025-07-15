from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('news/', views.ArticleListView.as_view(), name='article_list'),
    path('news/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('faq/', views.FAQListView.as_view(), name='faq_list'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('vacancies/', views.VacancyListView.as_view(), name='vacancy_list'),
    path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
] 