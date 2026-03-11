from rest_framework import serializers
from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    """Сериализатор для создания платежа."""
    course_id = serializers.IntegerField(min_value=1)

    def validate_course_id(self, value):
        from courses.models import Course
        if not Course.objects.filter(id=value, is_published=True).exists():
            raise serializers.ValidationError('Курс не найден или не опубликован')
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения платежа."""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_price = serializers.DecimalField(source='course.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'course_id', 'course_title', 'course_price',
            'amount', 'currency', 'status', 'payment_url', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'payment_url', 'created_at']
