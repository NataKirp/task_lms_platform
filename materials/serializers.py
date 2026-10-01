from django.template.context_processors import request
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from materials.models import Course, Lesson, Subscription
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
        allow_blank=True,
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
        allow_blank=True,
    )
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "owner",
            "description",
            "lessons_count",
            "lessons",
            "is_subscribed",
        ]

    def get_lessons_count(self, course) -> int:
        """
        Возвращает общее количество уроков, привязанных к данному курсу.
        """
        return course.lessons.count()

    def get_is_subscribed(self, course) -> bool:
        """
        Динамически определяет, подписан ли текущий пользователь на данный курс.
        """
        user = self.context.get("request").user
        if not request or user.is_anonymous:
            return False
        return bool(Subscription.objects.filter(user=user, course=course).exists())


class SubscriptionInputSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(
        help_text="Уникальный идентификатор (ID) курса, на который пользователь хочет подписаться или отписаться.")
