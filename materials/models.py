from django.db import models


class Course(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название", help_text="Укажите название курса"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Укажите описание курса",
    )
    preview = models.ImageField(
        upload_to="materials/images/courses/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название", help_text="Укажите название урока"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Укажите описание урока",
    )
    preview = models.ImageField(
        upload_to="materials/images/lessons/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Добавьте ссылку на видео",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Курс",
        help_text="Выберите курс",
        related_name="lessons",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name
