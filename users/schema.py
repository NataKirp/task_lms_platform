from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample, OpenApiParameter

user_viewset_schema  = extend_schema_view(
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
                    "city": "Москва"
                },
                request_only=True,
            )
        ]
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
            description="Фильтрация по методу оплаты: `cash` (наличные) или `bank_transfer` (перевод)."
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Кастомное количество элементов на одной странице пагинации (макс. 10)."
        ),
    ],
    tags=["Пользователи"]
)
