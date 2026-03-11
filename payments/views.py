# payments/views.py

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse

from courses.models import Course
from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentSerializer
from .services import stripe_service


@extend_schema(
    tags=['payments'],
    summary='Создать платёж для курса',
    description='Создаёт запись платежа и возвращает ссылку на оплату через Stripe',
    request=PaymentCreateSerializer,
    responses={
        201: PaymentSerializer,
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
    }
)
class CreatePaymentView(views.APIView):
    """View для создания платежа."""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']

        try:
            course = Course.objects.get(id=course_id, is_published=True)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден или не опубликован'},
                status=status.HTTP_404_NOT_FOUND
            )

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            currency=settings.STRIPE_CURRENCY,
            status='pending'
        )

        product_result = stripe_service.create_stripe_product(
            course_name=course.title,
            course_description=course.description or ''
        )
        if not product_result['success']:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': f'Ошибка создания продукта: {product_result["error"]}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment.stripe_product_id = product_result['product_id']

        price_result = stripe_service.create_stripe_price(
            product_id=product_result['product_id'],
            amount=float(course.price),
            currency=settings.STRIPE_CURRENCY
        )
        if not price_result['success']:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': f'Ошибка создания цены: {price_result["error"]}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment.stripe_price_id = price_result['price_id']

        domain = settings.DOMAIN_URL.rstrip('/')
        session_result = stripe_service.create_checkout_session(
            price_id=price_result['price_id'],
            success_url=f'{domain}/api/payments/success/?session_id={{CHECKOUT_SESSION_ID}}&payment_id={payment.id}',
            cancel_url=f'{domain}/api/payments/cancelled/?payment_id={payment.id}',
            customer_email=request.user.email,
            metadata={
                'payment_id': payment.id,
                'user_id': request.user.id,
                'course_id': course.id
            }
        )
        if not session_result['success']:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': f'Ошибка создания сессии: {session_result["error"]}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.stripe_session_id = session_result['session_id']
        payment.payment_url = session_result['url']
        payment.save()

        return Response(
            {
                **PaymentSerializer(payment).data,
                'payment_url': session_result['url']
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=['payments'],
    summary='Проверить статус платежа',
    description='Получает актуальный статус платежа из Stripe',
    parameters=[
        OpenApiParameter(
            name='payment_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID платежа в нашей системе'
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'payment_status': {'type': 'string'},
                'session_status': {'type': 'string'},
                'payment_url': {'type': 'string', 'nullable': True}
            }
        }
    }
)
class CheckPaymentStatusView(views.APIView):
    """View для проверки статуса платежа."""
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Платёж не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not payment.stripe_session_id:
            return Response(
                {'error': 'У платежа нет сессии Stripe'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = stripe_service.retrieve_session_status(payment.stripe_session_id)

        if not result['success']:
            return Response(
                {'error': f'Ошибка получения статуса: {result["error"]}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Опционально: обновляем статус в БД
        stripe_status = result['data'].payment_status
        if stripe_status == 'paid' and payment.status != 'paid':
            payment.status = 'paid'
            payment.save()

        return Response({
            'payment_id': payment.id,
            'payment_status': stripe_status,
            'session_status': result['data'].status,
            'payment_url': payment.payment_url,
            'course_title': payment.course.title
        })


class PaymentSuccessView(views.APIView):
    """Обработчик успешной оплаты (redirect от Stripe)."""
    permission_classes = []  # Доступ без авторизации

    def get(self, request):
        session_id = request.query_params.get('session_id')
        payment_id = request.query_params.get('payment_id')

        return JsonResponse({
            'status': 'success',
            'message': 'Оплата прошла успешно!',
            'payment_id': payment_id,
            'session_id': session_id
        })


class PaymentCancelledView(views.APIView):
    """Обработчик отменённой оплаты."""
    permission_classes = []

    def get(self, request):
        payment_id = request.query_params.get('payment_id')
        return JsonResponse({
            'status': 'cancelled',
            'message': 'Оплата была отменена',
            'payment_id': payment_id
        }, status=400)
