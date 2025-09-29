from django.contrib import admin
from .models import (
    Author, Genre, Publisher, Book, Customer, Order, OrderItem, Review, 
    SalesStatistics, UserSession, PickupPoint, PromoCode, Vacancy, 
    CompanyInfo, Article, Term, Employee, Banner, Partner, CompanyHistory, 
    CustomerReview, FAQ, Cart, CartItem
)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'price', 'quantity', 'created_at']
    list_filter = ['genres', 'publisher', 'created_at']
    search_fields = ['title', 'isbn']
    date_hierarchy = 'created_at'
    filter_horizontal = ['authors', 'genres']
    raw_id_fields = ['publisher']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']
    search_fields = ['user__username', 'phone']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'created_at', 'get_total_cost']
    list_filter = ['created_at']
    search_fields = ['customer__user__username']
    date_hierarchy = 'created_at'
    inlines = [
        type('OrderItemInline', (admin.TabularInline,), {
            'model': OrderItem,
            'extra': 0,
            'raw_id_fields': ['book'],
        })
    ]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'book', 'quantity', 'price', 'get_cost']
    list_filter = ['order__created_at']
    search_fields = ['book__title', 'order__customer__user__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'customer', 'rating', 'created_at', 'is_approved']
    list_filter = ['rating', 'created_at', 'is_approved']
    search_fields = ['book__title', 'customer__user__username']
    date_hierarchy = 'created_at'
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} review(s) approved.")
    approve_reviews.short_description = "Approve selected reviews"

@admin.register(SalesStatistics)
class SalesStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_orders', 'average_order_value', 'best_selling_book', 'best_selling_genre')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('total_sales', 'total_orders', 'average_order_value', 'best_selling_book', 'best_selling_genre')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_time', 'end_time', 'duration']
    list_filter = ['start_time', 'end_time']
    search_fields = ['user__username']
    date_hierarchy = 'start_time'
    readonly_fields = ['start_time', 'end_time', 'duration']

@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'address']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'active', 'valid_from', 'valid_to']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'salary', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'founded_year', 'updated_at']
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at']
    search_fields = ['title', 'summary']
    list_filter = ['published_at']

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['term', 'added_at']
    search_fields = ['term', 'definition']
    list_filter = ['added_at']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'phone', 'email']
    search_fields = ['name', 'position', 'phone', 'email']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    list_display = ['year', 'title']
    search_fields = ['title', 'description']
    ordering = ['-year']

@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['customer__user__username', 'title', 'text']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} review(s) approved.")
    approve_reviews.short_description = "Approve selected reviews"

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['category', 'is_published']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [
        type('CartItemInline', (admin.TabularInline,), {
            'model': CartItem,
            'extra': 0,
            'raw_id_fields': ['book'],
        })
    ]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'book', 'quantity', 'created_at']
    search_fields = ['cart__user__username', 'book__title']
    raw_id_fields = ['cart', 'book']
