from rest_framework import generics, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер для управления курсами.

    Обеспечивает стандартный CRUD-функционал. Доступен просмотр
    списка курсов вместе с их вложенными уроками.
    """

    serializer_class = CourseSerializer

    def get_queryset(self):
        """
        Динамическая фильтрация списка курсов.
        Модераторы и суперпользователи видят всё, обычные студенты — только свои курсы.
        """
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

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
            return [IsAuthenticated()]
        # Создавать курсы может авторизованный пользователь, но не модератор
        if self.action == "create":
            permission_classes = [IsAuthenticated, ~IsModer]
        # Просматривать список могут все авторизованные пользователи
        elif self.action == "list":
            permission_classes = [IsAuthenticated]
        # Детали и редактирование доступны модераторам ИЛИ владельцам курса
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        # Удалять курсы модератор не может, только владелец
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsOwner, ~IsModer]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Создание нового урока.

    Принимает параметры урока (название, описание, превью, ссылка на видео)
    и привязывает его к указанному курсу. Доступно любому авторизованному
    пользователю, кроме модераторов.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminUser | (~IsModer & IsAuthenticated)]

    def perform_create(self, serializer):
        """
        Автоматически назначает текущего авторизованного пользователя владельцем урока.
        """
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """
    Получение списка всех уроков.

    Возвращает перечень существующих уроков с базовой информацией.
    Модераторы видят весь список, владельцы только свои.
    """

    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Редактирование существующего урока.

    Позволяет полностью (PUT) или частично (PATCH) обновить данные урока
    по его идентификатору (ID).
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение детальной информации о конкретном уроке.

    Возвращает полные данные урока по его уникальному идентификатору (ID).
    Доступно модератору и владельцу.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsModer | IsOwner,)


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление урока.

    Безвозвратно удаляет объект урока из базы данных по его идентификатору (ID).
    Связанный курс при этом не удаляется.
    """

    queryset = Lesson.objects.all()
    permission_classes = [IsAdminUser | (IsOwner & ~IsModer)]
