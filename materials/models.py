from django.db import models

from config import settings


class Course(models.Model):
    """
    Хранит информацию о курсе.
    """

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
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Создатель",
        help_text="Укажите создателя курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """
    Хранит информацию об отдельном уроке, связанном с курсом :model:`materials.Course`.
    """

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
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Создатель",
        help_text="Укажите создателя урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Модель подписки на обновления курса.

    Обеспечивает связь между пользователем :model:`users.User` и курсом
    :model:`materials.Course`, позволяя отслеживать подписки на обновления
    учебных материалов. Уникальность связки гарантирует отсутствие
    дублирующих подписок.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
        help_text="Ссылка на пользователя, оформившего подписку",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс в подписке",
        help_text="Ссылка на курс, на который оформлена подписка",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} - {self.course.name}"
