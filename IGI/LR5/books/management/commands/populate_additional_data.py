from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import (
    Banner, Partner, CompanyHistory, CustomerReview, FAQ, 
    CompanyInfo, PromoCode, Cart, CartItem
)
from decimal import Decimal
import random
from django.utils import timezone
from datetime import timedelta, date

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate additional required data for the website'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating additional sample data...')

        # Create Company Info
        if not CompanyInfo.objects.exists():
            CompanyInfo.objects.create(
                name="HeavyShop Books",
                description="Belarus's premier online bookstore offering thousands of titles with fast delivery and excellent customer service. We've been serving book lovers since 2020.",
                founded_year=2020,
                requisites="""
                ИП "Тяжелый Магазин Книг"
                УНП: 123456789
                Свидетельство о регистрации: №12345
                Юридический адрес: г. Минск, ул. Примерная, 123
                Банковские реквизиты: 
                Р/с: BY12ALFA30143000080240000933
                Банк: ОАО "Альфа-Банк"
                БИК: ALFABY2X
                """
            )
            self.stdout.write('Company info created.')

        # Create Banners
        if not Banner.objects.exists():
            banners = [
                Banner.objects.create(
                    title="Summer Sale - Up to 50% Off",
                    description="Discover amazing deals on bestsellers and classics",
                    link="/books/",
                    is_active=True,
                    order=1
                ),
                Banner.objects.create(
                    title="New Arrivals - Fresh Reads",
                    description="Check out the latest additions to our catalog",
                    link="/books/?sort=-created_at",
                    is_active=True,
                    order=2
                ),
                Banner.objects.create(
                    title="Free Shipping on Orders Over 50 BYN",
                    description="Fast delivery to your doorstep",
                    is_active=True,
                    order=3
                ),
            ]
            self.stdout.write('Banners created.')

        # Create Partners
        if not Partner.objects.exists():
            partners = [
                Partner.objects.create(
                    name="Беларускі Дом Друку",
                    website="https://bdd.by",
                    description="Leading Belarusian publishing house",
                    is_active=True
                ),
                Partner.objects.create(
                    name="Народная Асвета",
                    website="https://uchebnik.by",
                    description="Educational literature publisher",
                    is_active=True
                ),
                Partner.objects.create(
                    name="Мастацкая Літаратура",
                    website="https://ml.by",
                    description="Fiction and literature publisher",
                    is_active=True
                ),
                Partner.objects.create(
                    name="Технопринт",
                    website="https://technoprint.by",
                    description="Technical and scientific literature",
                    is_active=True
                ),
                Partner.objects.create(
                    name="Книжный Дом",
                    website="https://bookhouse.by",
                    description="Book distribution network",
                    is_active=True
                ),
                Partner.objects.create(
                    name="Аверсэв",
                    website="https://aversev.by",
                    description="Educational materials publisher",
                    is_active=True
                ),
            ]
            self.stdout.write('Partners created.')

        # Create Company History
        if not CompanyHistory.objects.exists():
            history = [
                CompanyHistory.objects.create(
                    year=2020,
                    title="Foundation",
                    description="HeavyShop was founded with a mission to make quality books accessible to everyone in Belarus. Started with a small catalog of 500 titles."
                ),
                CompanyHistory.objects.create(
                    year=2021,
                    title="Expansion",
                    description="Expanded our catalog to over 2,000 titles and launched our mobile-friendly website. Introduced same-day delivery in Minsk."
                ),
                CompanyHistory.objects.create(
                    year=2022,
                    title="Digital Innovation",
                    description="Launched our REST API and mobile app. Introduced digital books and audiobooks to our catalog."
                ),
                CompanyHistory.objects.create(
                    year=2023,
                    title="Growth",
                    description="Reached 10,000+ books in catalog. Expanded delivery to all major cities in Belarus. Launched customer loyalty program."
                ),
                CompanyHistory.objects.create(
                    year=2024,
                    title="Excellence",
                    description="Won 'Best Online Bookstore' award. Introduced AI-powered book recommendations and advanced search features."
                ),
                CompanyHistory.objects.create(
                    year=2025,
                    title="Future Ready",
                    description="Implementing sustainable packaging and carbon-neutral delivery. Expanding into educational technology and interactive learning materials."
                ),
            ]
            self.stdout.write('Company history created.')

        # Create Customer Reviews
        if not CustomerReview.objects.exists():
            from books.models import Customer
            customers = list(Customer.objects.all())
            
            reviews_data = [
                {
                    'rating': 5,
                    'title': 'Excellent Service',
                    'text': 'Fast delivery, great packaging, and amazing book selection. Highly recommend HeavyShop!'
                },
                {
                    'rating': 4,
                    'title': 'Good Experience',
                    'text': 'Easy to navigate website and quick order processing. Will definitely order again.'
                },
                {
                    'rating': 5,
                    'title': 'Best Bookstore',
                    'text': 'Been a customer for 2 years. Always satisfied with the quality and service.'
                },
                {
                    'rating': 4,
                    'title': 'Great Selection',
                    'text': 'Found many rare books that I could not find elsewhere. Customer service is helpful.'
                },
                {
                    'rating': 5,
                    'title': 'Perfect!',
                    'text': 'Books arrived in perfect condition. Love the loyalty program and discounts.'
                }
            ]
            
            for i, review_data in enumerate(reviews_data):
                if i < len(customers):
                    CustomerReview.objects.create(
                        customer=customers[i],
                        is_approved=True,
                        **review_data
                    )
            self.stdout.write('Customer reviews created.')

        # Create FAQ
        if not FAQ.objects.exists():
            faqs = [
                FAQ.objects.create(
                    question="How long does delivery take?",
                    answer="Standard delivery takes 2-3 business days within Minsk and 3-5 business days to other cities. Same-day delivery is available in Minsk for orders placed before 2 PM.",
                    category="Delivery",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="Do you accept returns?",
                    answer="Yes, we accept returns within 14 days of purchase. Books must be in original condition. Please contact our customer service for return instructions.",
                    category="Returns",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="What payment methods do you accept?",
                    answer="We accept all major credit cards, bank transfers, and cash on delivery. Online payments are processed securely through our payment gateway.",
                    category="Payment",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="How can I track my order?",
                    answer="Once your order is shipped, you'll receive an email with tracking information. You can also check your order status in your account dashboard.",
                    category="Orders",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="Do you have a mobile app?",
                    answer="Yes! Our mobile app is available for both iOS and Android. Download it from the App Store or Google Play for a better shopping experience.",
                    category="Technology",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="How do I use promocodes?",
                    answer="Enter your promocode at checkout in the 'Promo Code' field. The discount will be applied automatically to eligible items.",
                    category="Promocodes",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="Can I cancel my order?",
                    answer="Orders can be cancelled within 1 hour of placement if they haven't been processed yet. After that, please contact customer service.",
                    category="Orders",
                    is_published=True
                ),
                FAQ.objects.create(
                    question="Do you offer gift cards?",
                    answer="Yes, we offer digital gift cards in various denominations. Perfect for book lovers! Purchase them through your account.",
                    category="Gift Cards",
                    is_published=True
                ),
            ]
            self.stdout.write('FAQ entries created.')

        # Create Promocodes
        if not PromoCode.objects.exists():
            today = timezone.now().date()
            promocodes = [
                PromoCode.objects.create(
                    code="WELCOME10",
                    discount_percent=10,
                    active=True,
                    valid_from=today - timedelta(days=30),
                    valid_to=today + timedelta(days=60)
                ),
                PromoCode.objects.create(
                    code="SUMMER25",
                    discount_percent=25,
                    active=True,
                    valid_from=today - timedelta(days=15),
                    valid_to=today + timedelta(days=45)
                ),
                PromoCode.objects.create(
                    code="BOOKWORM15",
                    discount_percent=15,
                    active=True,
                    valid_from=today,
                    valid_to=today + timedelta(days=90)
                ),
                PromoCode.objects.create(
                    code="EXPIRED20",
                    discount_percent=20,
                    active=False,
                    valid_from=today - timedelta(days=90),
                    valid_to=today - timedelta(days=30)
                ),
                PromoCode.objects.create(
                    code="STUDENT20",
                    discount_percent=20,
                    active=True,
                    valid_from=today - timedelta(days=7),
                    valid_to=today + timedelta(days=120)
                ),
            ]
            self.stdout.write('Promocodes created.')

        self.stdout.write(self.style.SUCCESS('Successfully populated all additional data!'))