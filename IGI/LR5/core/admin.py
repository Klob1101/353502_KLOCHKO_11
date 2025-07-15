from django.contrib import admin
from .models import Article, CompanyInfo, FAQ, Employee, Vacancy, Promotion

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'is_published']
    list_filter = ['is_published', 'created_at', 'author']
    search_fields = ['title', 'content', 'summary']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['year', 'video_url']
    ordering = ['year']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_at', 'order']
    list_filter = ['created_at']
    search_fields = ['question', 'answer']
    ordering = ['order', 'created_at']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'department', 'phone', 'email']
    list_filter = ['department', 'hire_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'position', 'bio']
    date_hierarchy = 'hire_date'
    ordering = ['department', 'user__last_name']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['birth_date'].help_text = 'Employee must be at least 18 years old'
        return form

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'salary_min', 'salary_max', 'is_active']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['title', 'description', 'requirements']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'start_date', 'end_date', 'is_active', 'current_uses', 'max_uses']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['code', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('code', 'current_uses')
        return ('current_uses',)
