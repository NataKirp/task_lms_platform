from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from users.models import Payment
from users.serializers import PaymentSerializer


class PaymentListAPIView(generics.ListAPIView):
    """
    Получение списка всех платежей.

    Возвращает перечень платежей с базовой информацией.
    Позволяет администраторам и пользователям просматривать историю оплат.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["payment_method", "course_paid", "single_lesson_paid"]
    ordering_fields = ["payment_date",]
