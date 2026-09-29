from rest_framework.fields import SerializerMethodField
from rest_framework import serializers

from materials.models import Course, Lesson
from materials.validators import validate_youtube_only


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели урока.

    Обеспечивает валидацию и преобразование данных урока, включая валидацию
    внешнего ключа связи с родительским курсом.
    """

    video_url = serializers.CharField(
        validators=[validate_youtube_only],
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели курса.

    Выводит базовую информацию о курсе и автоматически рассчитывает
    общее количество связанных с ним уроков и детальную информацию по всем урокам одновременно.
    """

    description = serializers.CharField(
        validators=[validate_youtube_only],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "owner", "description", "lessons_count", "lessons"]

    def get_lessons_count(self, course):
        """
        Возвращает общее количество уроков, привязанных к данному курсу.
        """
        return course.lessons.count()
