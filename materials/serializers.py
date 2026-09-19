from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    """
    Сериализатор для модели курса.

    Используется для полного преобразования данных курса (включая ID, название,
    описание и превью) в формат JSON при чтении и записи.
    """
    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(ModelSerializer):
    """
    Сериализатор для модели урока.

    Обеспечивает валидацию и преобразование данных урока, включая валидацию
    внешнего ключа связи с родительским курсом.
    """
    class Meta:
        model = Lesson
        fields = "__all__"
