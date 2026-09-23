from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from users.models import Payment, User
from users.permissions import IsAccountOwner
from users.serializers import (PaymentSerializer, UserProfileSerializer,
                               UserReadOnlySerializer, UserRegisterSerializer)


class UserViewSet(ModelViewSet):
    """
    ViewSet для управления пользователями (CRUD).

    Обеспечивает регистрацию, просмотр, редактирование и удаление профилей.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            if self.get_object() == self.request.user or self.request.user.is_superuser:
                return UserProfileSerializer
        return UserReadOnlySerializer

    def get_permissions(self):
        if self.request.user and self.request.user.is_superuser:
            return [IsAuthenticated()]
        elif self.action == "create":
            # super().get_permissions() ожидает, что элементы внутри этого кортежа являются объектами
            # (экземплярами классов), а не самими классами. То есть нужно инициализировать класс скобками: AllowAny()
            return [AllowAny()]
        elif self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAccountOwner()]
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
    ordering_fields = ["payment_date"]
