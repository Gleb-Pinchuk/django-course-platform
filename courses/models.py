from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Course(models.Model):
    """
    Модель курса.
    """
    title = models.CharField(max_length=200, verbose_name='Название курса')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    is_published = models.BooleanField(default=False, verbose_name='Опубликован')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    last_notified_at = models.DateTimeField(null=True, blank=True, verbose_name='Последнее уведомление')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def can_send_notification(self):
        """
        Проверяет, прошло ли более 4 часов с последнего уведомления.
        Дополнительное задание: уведомление только если курс не обновлялся более 4 часов.
        """
        if self.last_notified_at is None:
            return True

        four_hours_ago = timezone.now() - timedelta(hours=4)
        return self.last_notified_at < four_hours_ago

    def mark_notified(self):
        """Обновляет время последнего уведомления."""
        self.last_notified_at = timezone.now()
        self.save(update_fields=['last_notified_at'])


class Subscription(models.Model):
    """
    Подписка пользователя на обновления курса.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Курс'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']

    def __str__(self):
        return f'{self.user.email} -> {self.course.title}'
