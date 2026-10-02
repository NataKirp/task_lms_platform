from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema, extend_schema_view)
from rest_framework import status

from users.serializers import PaymentSerializer

user_viewset_schema = extend_schema_view(
    create=extend_schema(
        summary="Создать нового пользователя",
        description=(
            "Регистрация нового пользователя платформы. "
            "Переданный пароль автоматически хэшируется на сервере перед сохранением в базу данных."
        ),
        examples=[
            OpenApiExample(
                name="Пример успешной регистрации",
                value={
                    "email": "student@sky.pro",
                    "password": "strong_password_123",
                    "phone_number": "+79991112233",
                    "city": "Москва",
                },
                request_only=True,
            )
        ],
    ),
    list=extend_schema(summary="Получить список всех пользователей"),
    retrieve=extend_schema(summary="Детальная информация о пользователе"),
    update=extend_schema(summary="Изменить пользователя"),
    partial_update=extend_schema(summary="Частичное изменить пользователя"),
    destroy=extend_schema(summary="Удалить пользователя"),
)
payment_list_schema = extend_schema(
    summary="Получить список платежей",
    parameters=[
        OpenApiParameter(
            name="payment_method",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Фильтрация по методу оплаты: `cash` (наличные) или `bank_transfer` (перевод).",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Кастомное количество элементов на одной странице пагинации (макс. 10).",
        ),
    ],
    tags=["Платежи"],
)
payment_stripe_schema = extend_schema(
    summary="Создание сессии оплаты курса через Stripe",
    description="Принимает ID курса, генерирует платежную ссылку Stripe, возвращает данные платежа и регистрирует транзакцию в базе данных.",
    responses={201: PaymentSerializer},
    examples=[
        OpenApiExample(
            name="Пример запроса", value={"course_id": 1}, request_only=True
        ),
        OpenApiExample(
            name="Пример успешного ответа сервера",
            value={
                "id": 42,
                "payment_date": "2026-10-01T23:45:00Z",
                "amount": "5000.00",
                "payment_method": "stripe",
                "stripe_session_id": "cs_test_a1B2c3D4...",
                "stripe_link": "https://stripe.com_...",
                "status": "pending",
                "user": 1,
                "course_paid": 1,
                "single_lesson_paid": None,
            },
            response_only=True,
            status_codes=[str(status.HTTP_201_CREATED)],
        ),
    ],
    tags=["Платежи"],
)
payment_stripe_status_schema = extend_schema(
    summary="Проверка и обновление актуального статуса платежа через Stripe",
    description="При просмотре деталей платежа обращается к Stripe, проверяет статус транзакции и обновляет поле status в базе данных.",
    tags=["Платежи"],
)
