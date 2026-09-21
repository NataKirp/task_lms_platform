from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    """
    Сериализатор для модели урока.

    Обеспечивает валидацию и преобразование данных урока, включая валидацию
    внешнего ключа связи с родительским курсом.
    """

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    """
    Сериализатор для модели курса.

    Выводит базовую информацию о курсе и автоматически рассчитывает
    общее количество связанных с ним уроков и детальную информацию по всем урокам одновременно.
    """
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "description", "lessons_count", "lessons"]

    def get_lessons_count(self, course):
        """
        Возвращает общее количество уроков, привязанных к данному курсу.
        """
        return course.lessons.count()
