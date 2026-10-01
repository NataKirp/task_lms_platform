from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample, inline_serializer

from materials.serializers import SubscriptionInputSerializer

course_viewset_schema = extend_schema_view(
    create=extend_schema(summary="Создать новый курс"),
    list=extend_schema(summary="Получить список всех курсов"),
    retrieve=extend_schema(summary="Детальная информация о курсе"),
    update = extend_schema(summary="Изменить курс"),
    partial_update = extend_schema(summary="Частично изменить курс"),
    destroy = extend_schema(summary="Удалить курс"),
    )
lesson_create_schema = extend_schema(
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
    ],
    tags=["Уроки"]
)
lesson_list_schema = extend_schema(summary="Получить список всех уроков", tags=["Уроки"])
lesson_retrieve_schema = extend_schema(summary="Детальная информация об уроке", tags=["Уроки"])
lesson_update_schema = extend_schema(summary="Изменить урок", tags=["Уроки"])
lesson_destroy_schema = extend_schema(summary="Удалить урок", tags=["Уроки"])

subscription_manage_schema = extend_schema(
    summary="Управление подпиской на курс",
    description="Эндпойнт-переключатель. Если подписки нет — создаёт её, если есть — удаляет.",
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={"course_id": 1},
            request_only=True
        ),
        OpenApiExample(
            name="Пример успешного ответа сервера",
            value={"message": "Подписка успешно добавлена"},
            response_only=True,
            status_codes=[str(status.HTTP_200_OK)]
        )
    ],
    tags=["Курсы"]
)
