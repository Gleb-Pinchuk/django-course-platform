from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/', views.CreatePaymentView.as_view(), name='create'),
    path('<int:payment_id>/status/', views.CheckPaymentStatusView.as_view(), name='status'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('cancelled/', views.PaymentCancelledView.as_view(), name='cancelled'),
]
