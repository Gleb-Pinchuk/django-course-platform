from django.db import models
from django.conf import settings
from courses.models import Course


class Payment(models.Model):
    """
    Модель платежа.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
        ('failed', 'Ошибка'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')

    # Данные Stripe
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)

    payment_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на оплату')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    currency = models.CharField(max_length=3, default='usd', verbose_name='Валюта')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']


    def __str__(self):
        return f'Payment #{self.id} - {self.user.email} - {self.course.title}'
