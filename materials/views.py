from datetime import datetime

from django.db.models import Q  # Импортируем оператор Q для сложных запросов
from drf_spectacular.utils import extend_schema
from rest_framework import generics, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.pagination import CustomPagination
from materials.schema import (course_viewset_schema, lesson_create_schema,
                              lesson_destroy_schema, lesson_list_schema,
                              lesson_retrieve_schema, lesson_update_schema,
                              subscription_manage_schema)
from materials.serializers import (CourseSerializer, LessonSerializer,
                                   SubscriptionInputSerializer)
from materials.tasks import send_course_update_email
from users.permissions import IsModer, IsOwner


@extend_schema(tags=["Курсы"])
@course_viewset_schema
class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер для управления курсами.

    Обеспечивает стандартный CRUD-функционал. Доступен просмотр
    списка курсов вместе с их вложенными уроками.
    """

    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Динамическая фильтрация списка курсов.
        Модераторы и суперпользователи видят всё, обычные студенты — только свои курсы.
        """
        # Защита от AnonymousUser при генерации схемы Swagger
        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()

        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()
        return Course.objects.filter(
            Q(owner=user) | Q(subscriptions__user=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        Автоматически назначает текущего авторизованного пользователя владельцем курса.
        """
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Разграничивает права доступа к операциям с курсами для модераторов.
        """
        # Если это суперпользователь — даем полный доступ без проверок
        if self.request.user and self.request.user.is_superuser:
            return [IsAdminUser()]
        # Создавать курсы может авторизованный пользователь, но не модератор
        if self.action == "create":
            permission_classes = [~IsModer]
        # Просматривать список могут все авторизованные пользователи
        elif self.action == "list":
            permission_classes = [IsAuthenticated]
        # Детали и редактирование доступны модераторам ИЛИ владельцам курса
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsModer | IsOwner]
        # Удалять курсы модератор не может, только владелец
        elif self.action == "destroy":
            permission_classes = [IsOwner | ~IsModer]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        """
        Сохраняет изменения курса и автоматически рассылает
        уведомления об обновлении всем подписанным пользователям через Celery.
        """
        course_item = serializer.save()
        subs_items = Subscription.objects.filter(course=course_item)

        if subs_items.exists():
            for sub in subs_items:
                if sub.user.email:
                    send_course_update_email.delay(sub.user.email, course_item.name)


@lesson_create_schema
class LessonCreateAPIView(generics.CreateAPIView):
    """
    Создание нового урока.

    Принимает параметры урока (название, описание, превью, ссылка на видео)
    и привязывает его к указанному курсу. Автоматически рассылает
    уведомления всем подписчикам этого курса через Celery.
    Доступно любому авторизованному пользователю, кроме модераторов.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (~IsModer,)

    def perform_create(self, serializer):
        """
        Автоматически назначает текущего авторизованного пользователя владельцем урока и рассылает
        уведомления всем подписчикам курса, в который входит урок, через Celery.
        """
        lesson_item = serializer.save(owner=self.request.user)
        course_item = lesson_item.course

        if course_item:
            course_item.save()
            subs_items = Subscription.objects.filter(course=course_item)

            if subs_items.exists():
                for sub in subs_items:
                    if sub.user.email:
                        send_course_update_email.delay(sub.user.email, course_item.name)


@lesson_list_schema
class LessonListAPIView(generics.ListAPIView):
    """
    Получение списка всех уроков.

    Возвращает перечень существующих уроков с базовой информацией.
    Модераторы видят весь список, владельцы только свои.
    """

    serializer_class = LessonSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Защита от AnonymousUser при генерации схемы Swagger
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()

        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


@lesson_update_schema
class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Редактирование существующего урока.

    Позволяет полностью (PUT) или частично (PATCH) обновить данные урока
    по его идентификатору (ID).
    При изменении урока автоматически уведомляет подписчиков курса, в который входит урок, через Celery.
    Доступно модератору и владельцу.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)

    def perform_update(self, serializer):
        """
        Если урок входит в курс, сохраняет изменения курса и автоматически рассылает
        уведомления об обновлении всем подписанным пользователям через Celery.
        """
        lesson_item = serializer.save()
        course_item = lesson_item.course

        if course_item:
            course_item.save()
            subs_items = Subscription.objects.filter(course=course_item)

            if subs_items.exists():
                for sub in subs_items:
                    if sub.user.email:
                        send_course_update_email.delay(sub.user.email, course_item.name)


@lesson_retrieve_schema
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение детальной информации о конкретном уроке.

    Возвращает полные данные урока по его уникальному идентификатору (ID).
    Доступно модератору и владельцу.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)


@lesson_destroy_schema
class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление урока.

    Безвозвратно удаляет объект урока из базы данных по его идентификатору (ID).
    Связанный курс при этом не удаляется.
    Удалять курсы модератор не может, только владелец.
    """

    queryset = Lesson.objects.all()
    serializer_class = (
        LessonSerializer  # Добавлен сериализатор, чтобы Swagger его прочитал
    )
    permission_classes = (IsOwner | ~IsModer,)


class SubscriptionAPIView(APIView):
    """
    Контроллер управления подпиской на курс (Установка / Снятие).
    """

    serializer_class = SubscriptionInputSerializer

    @subscription_manage_schema
    def post(self, request, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get("course_id")
        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)
        if subs_item.exists():
            subs_item.delete()
            message = "Подписка успешно удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка успешно добавлена"
        return Response({"message": message})
