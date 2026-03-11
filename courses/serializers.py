from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    """
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'is_published', 'created_at']
        read_only_fields = ['id', 'created_at']
