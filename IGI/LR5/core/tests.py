from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from .models import Article, CompanyInfo, FAQ, Employee, Vacancy, Promotion

User = get_user_model()

class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Test Content',
            summary='Test Summary',
            author=self.user,
            is_published=True
        )

    def test_article_str(self):
        self.assertEqual(str(self.article), 'Test Article')

    def test_article_ordering(self):
        article2 = Article.objects.create(
            title='Test Article 2',
            content='Test Content 2',
            summary='Test Summary 2',
            author=self.user,
            is_published=True
        )
        articles = Article.objects.all()
        self.assertEqual(articles[0], article2)
        self.assertEqual(articles[1], self.article)

class CompanyInfoModelTest(TestCase):
    def setUp(self):
        self.info = CompanyInfo.objects.create(
            year=2020,
            description='Test Description',
            requisites='Test Requisites'
        )

    def test_company_info_str(self):
        self.assertEqual(str(self.info), 'Company Info - 2020')

    def test_company_info_ordering(self):
        info2 = CompanyInfo.objects.create(
            year=2019,
            description='Test Description 2'
        )
        infos = CompanyInfo.objects.all()
        self.assertEqual(infos[0], info2)
        self.assertEqual(infos[1], self.info)

class FAQModelTest(TestCase):
    def setUp(self):
        self.faq = FAQ.objects.create(
            question='Test Question',
            answer='Test Answer',
            order=1
        )

    def test_faq_str(self):
        self.assertEqual(str(self.faq), 'Test Question')

    def test_faq_ordering(self):
        faq2 = FAQ.objects.create(
            question='Test Question 2',
            answer='Test Answer 2',
            order=0
        )
        faqs = FAQ.objects.all()
        self.assertEqual(faqs[0], faq2)
        self.assertEqual(faqs[1], self.faq)

class EmployeeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.employee = Employee.objects.create(
            user=self.user,
            position='Test Position',
            department='Test Department',
            bio='Test Bio',
            phone='+375 (29) 123-45-67',
            email='test@example.com',
            birth_date=date(2000, 1, 1),
            hire_date=timezone.now().date()
        )

    def test_employee_str(self):
        self.assertEqual(str(self.employee), 'testuser - Test Position')

class VacancyModelTest(TestCase):
    def setUp(self):
        self.vacancy = Vacancy.objects.create(
            title='Test Vacancy',
            department='Test Department',
            description='Test Description',
            requirements='Test Requirements',
            salary_min=1000,
            salary_max=2000,
            is_active=True
        )

    def test_vacancy_str(self):
        self.assertEqual(str(self.vacancy), 'Test Vacancy (Test Department)')

class PromotionModelTest(TestCase):
    def setUp(self):
        self.promotion = Promotion.objects.create(
            code='TEST123',
            description='Test Description',
            discount_percent=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            max_uses=100
        )

    def test_promotion_str(self):
        self.assertEqual(str(self.promotion), 'TEST123 (10% off)')

    def test_promotion_is_valid(self):
        self.assertTrue(self.promotion.is_valid())
        self.promotion.current_uses = self.promotion.max_uses
        self.promotion.save()
        self.assertFalse(self.promotion.is_valid())

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Test Content',
            summary='Test Summary',
            author=self.user,
            is_published=True
        )

    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'Test Article')

    def test_about_view(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_article_list_view(self):
        response = self.client.get(reverse('core:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/article_list.html')
        self.assertContains(response, 'Test Article')

    def test_article_detail_view(self):
        response = self.client.get(
            reverse('core:article_detail', args=[self.article.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/article_detail.html')
        self.assertContains(response, 'Test Article')

    def test_faq_list_view(self):
        response = self.client.get(reverse('core:faq_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/faq_list.html')

    def test_contacts_view(self):
        response = self.client.get(reverse('core:contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contacts.html')

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('core:privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/privacy_policy.html')

    def test_vacancy_list_view(self):
        response = self.client.get(reverse('core:vacancy_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/vacancy_list.html')

    def test_promotion_list_view(self):
        response = self.client.get(reverse('core:promotion_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/promotion_list.html')
