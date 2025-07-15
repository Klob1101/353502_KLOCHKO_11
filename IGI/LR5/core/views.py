from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import timezone
from .models import Article, CompanyInfo, FAQ, Employee, Vacancy, Promotion

# Create your views here.

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем последнюю опубликованную статью
        context['latest_article'] = Article.objects.filter(
            is_published=True
        ).first()
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_history'] = CompanyInfo.objects.all()
        return context

class ArticleListView(ListView):
    model = Article
    template_name = 'core/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(is_published=True)

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'core/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(is_published=True)

class FAQListView(ListView):
    model = FAQ
    template_name = 'core/faq_list.html'
    context_object_name = 'faqs'

class ContactsView(ListView):
    model = Employee
    template_name = 'core/contacts.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return Employee.objects.select_related('user')

class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'

class VacancyListView(ListView):
    model = Vacancy
    template_name = 'core/vacancy_list.html'
    context_object_name = 'vacancies'

    def get_queryset(self):
        return Vacancy.objects.filter(is_active=True)

class PromotionListView(ListView):
    model = Promotion
    template_name = 'core/promotion_list.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
