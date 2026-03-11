import stripe
from django.conf import settings
from typing import Optional, Dict, Any

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course_name: str, course_description: str) -> Dict[str, Any]:
    """Создаёт продукт в Stripe."""
    try:
        product = stripe.Product.create(
            name=course_name,
            description=course_description,
            metadata={'source': 'django_course_platform'}
        )
        return {
            'success': True,
            'product_id': product.id,
            'data': product
        }
    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_stripe_price(product_id: str, amount: float, currency: str = 'usd') -> Dict[str, Any]:
    """Создаёт цену в Stripe (в копейках/центах)."""
    try:
        amount_in_cents = int(amount * 100)
        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount_in_cents,
            currency=currency,
        )
        return {
            'success': True,
            'price_id': price.id,
            'data': price
        }
    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """Создаёт сессию оплаты Stripe Checkout."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata=metadata or {},
        )
        return {
            'success': True,
            'session_id': session.id,
            'url': session.url,
            'data': session
        }
    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e)
        }


def retrieve_session_status(session_id: str) -> Dict[str, Any]:
    """Получает статус сессии по ID."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'success': True,
            'status': session.payment_status,
            'session_status': session.status,
            'data': session
        }
    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e)
        }
