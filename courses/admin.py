from django.contrib import admin
from .models import Course, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'created_at']
    list_filter = ['created_at', 'course']
    search_fields = ['user__email', 'course__title']