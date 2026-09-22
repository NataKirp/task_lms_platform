from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserRegisterSerializer, UserProfileSerializer, UserReadOnlySerializer


class UserViewSet(ModelViewSet):
    """
    ViewSet для управления пользователями (CRUD).

    Обеспечивает регистрацию, просмотр, редактирование и удаление профилей.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        if self.action in ["retrieve", "update", "partial_update"]:
            if self.get_object() == self.request.user or self.request.user.is_superuser:
                return UserProfileSerializer
        return UserReadOnlySerializer

    def get_permissions(self):
        if self.action == "create":
            # super().get_permissions() ожидает, что элементы внутри этого кортежа являются объектами
            # (экземплярами классов), а не самими классами. То есть нужно инициализировать класс скобками: AllowAny()
            return [AllowAny()]
        return super().get_permissions()


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
    ordering_fields = ["payment_date", ]
