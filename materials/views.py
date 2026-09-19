from rest_framework import generics, viewsets

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Контроллер для управления курсами.

    Обеспечивает стандартный CRUD-функционал. Доступен просмотр
    списка курсов вместе с их вложенными уроками.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Создание нового урока.

    Принимает параметры урока (название, описание, превью, ссылка на видео)
    и привязывает его к указанному курсу.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonListAPIView(generics.ListAPIView):
    """
    Получение списка всех уроков.

    Возвращает перечень существующих уроков с базовой информацией.
    Позволяет администраторам и пользователям просматривать доступные материалы.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Редактирование существующего урока.

    Позволяет полностью (PUT) или частично (PATCH) обновить данные урока
    по его идентификатору (ID).
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение детальной информации о конкретном уроке.

    Возвращает полные данные урока по его уникальному идентификатору (ID).
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление урока.

    Безвозвратно удаляет объект урока из базы данных по его идентификатору (ID).
    Связанный курс при этом не удаляется.
    """
    queryset = Lesson.objects.all()
