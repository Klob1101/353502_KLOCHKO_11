from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
import datetime

User = get_user_model()

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(help_text="One sentence summary of the article")
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class CompanyInfo(models.Model):
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900)])
    description = models.TextField()
    logo = models.ImageField(upload_to='company/', null=True, blank=True)
    video_url = models.URLField(blank=True)
    requisites = models.TextField(blank=True)

    def __str__(self):
        return f"Company Info - {self.year}"

    class Meta:
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"
        ordering = ['year']

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    birth_date = models.DateField()
    hire_date = models.DateField()
    photo = models.ImageField(upload_to='employees/', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.position}'

    def save(self, *args, **kwargs):
        if self.birth_date:
            age = (timezone.now().date() - self.birth_date).days // 365
            if age < 18:
                raise ValueError('Employee must be at least 18 years old.')
        super().save(*args, **kwargs)

    def age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.birth_date:
            age = self.age()
            if age < 18:
                raise ValidationError('Employee must be at least 18 years old.')

    class Meta:
        ordering = ['department', 'user__last_name']

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.department})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"

class Promotion(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    discount_percent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_uses = models.PositiveIntegerField()
    current_uses = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} ({self.discount_percent}% off)'

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now and
            self.end_date >= now and
            self.current_uses < self.max_uses
        )

    class Meta:
        ordering = ['-created_at']
