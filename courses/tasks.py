from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription


@shared_task
def debug_task():
    """Тестовая задача для проверки работы Celery."""
    print('Celery is working! ✅')
    return {'status': 'success', 'message': 'Celery task executed successfully'}


@shared_task
def send_course_update_email(subscription_id, course_title, course_url):
    """
    Отправляет email подписчику об обновлении курса.
    """
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subject = f'Обновление курса: {course_title}'
        message = f'''
        Здравствуйте, {subscription.user.email}!

        Курс "{course_title}" был обновлён.

        Перейдите по ссылке, чтобы посмотреть новые материалы:
        {course_url}

        С уважением,
        Команда платформы
        '''
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [subscription.user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return {'status': 'success', 'email': subscription.user.email}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_course_update_notifications(course_id):
    """
    Отправляет уведомления всем подписчикам курса об обновлении.
    Вызывается при обновлении курса.
    """
    from .models import Course, Subscription

    try:
        course = Course.objects.get(id=course_id)
        course_url = f'{settings.DOMAIN_URL}/api/courses/{course.id}/'

        # Получаем всех подписчиков курса
        subscriptions = Subscription.objects.filter(course=course)

        results = []
        for subscription in subscriptions:
            # Отправляем задачу на отправку email асинхронно
            result = send_course_update_email.delay(
                subscription_id=subscription.id,
                course_title=course.title,
                course_url=course_url
            )
            results.append({
                'user': subscription.user.email,
                'task_id': result.id
            })

        return {
            'status': 'success',
            'course_id': course_id,
            'notifications_sent': len(results),
            'details': results
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более 30 дней.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    thirty_days_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(
        last_login__lt=thirty_days_ago,
        is_active=True
    ).exclude(
        is_staff=True
    )

    deactivated_count = inactive_users.update(is_active=False)

    return {
        'status': 'success',
        'deactivated_count': deactivated_count,
        'timestamp': timezone.now().isoformat()
    }
