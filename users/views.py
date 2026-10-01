from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import Payment, User
from users.permissions import IsAccountOwner
from users.schema import (payment_list_schema, payment_stripe_schema,
                          payment_stripe_status_schema, user_viewset_schema)
from users.serializers import (PaymentSerializer,
                               StripePaymentCreateSerializer,
                               UserProfileSerializer, UserReadOnlySerializer,
                               UserRegisterSerializer)
from users.services import check_stripe_payment_status, create_stripe_session


@extend_schema(tags=["Пользователи"])
@user_viewset_schema
class UserViewSet(ModelViewSet):
    """
    ViewSet для управления пользователями (CRUD).

    Обеспечивает регистрацию, просмотр, редактирование и удаление профилей.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        # для swagger
        if getattr(self, "swagger_fake_view", False):
            if self.action == "create":
                return UserRegisterSerializer
            elif self.action in ["retrieve", "update", "partial_update"]:
                return UserProfileSerializer
            return UserReadOnlySerializer

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


@payment_list_schema
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


@payment_stripe_schema
class PaymentStripeCreateAPIView(CreateAPIView):
    """
    Создание сессии оплаты курса через Stripe.

    Принимает ID курса, генерирует платежную ссылку Stripe
    и регистрирует транзакцию в базе данных со статусом 'pending'.
    """

    queryset = Payment.objects.all()
    serializer_class = StripePaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = serializer.validated_data.get("course_id")
        payment_obj = create_stripe_session(user=self.request.user, course_id=course_id)
        response_serializer = PaymentSerializer(payment_obj)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@payment_stripe_status_schema
class PaymentStripeStatusRetrieveAPIView(RetrieveAPIView):
    """
    Проверка и обновление актуального статуса платежа через Stripe.

    При просмотре деталей платежа бэкенд обращается к Stripe,
    проверяет статус транзакции и обновляет поле status в базе данных.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_object(self):
        payment = super().get_object()

        if payment.status == "completed":
            return payment
        # Если статус "pending" проверяем его в Stripe по сохраненному stripe_session_id
        if payment.stripe_session_id:
            new_status = check_stripe_payment_status(payment.stripe_session_id)
            if new_status != payment.status:
                payment.status = new_status
                payment.save()
        return payment
