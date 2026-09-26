from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """
    Кастомная модель пользователя системы обучения.

    Авторизация в системе происходит по адресу электронной почты вместо username.
    Хранит личные данные пользователя: аватар, контактный телефон и город проживания.
    """

    username = None

    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Укажите эл.почту"
    )
    phone_number = PhoneNumberField(
        unique=True,
        region="RU",
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите номер телефона",
    )
    city = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Введите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите свой аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """
    Хранит информацию об оплате курсов или уроков пользователями :model:`users.User`.
    """

    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("bank_transfer", "Перевод на счет"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
        help_text="Выберите пользователя, совершившего платеж",
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты",
        help_text="Дата и время проведения платежа",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        help_text="Укажите сумму платежа",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
    )
    course_paid = models.ForeignKey(
        "materials.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="course_payments",
        verbose_name="Оплаченный курс",
        help_text="Укажите оплаченный курс (если применим)",
    )
    single_lesson_paid = models.ForeignKey(
        "materials.Lesson",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lesson_payments",
        verbose_name="Оплаченный урок",
        help_text="Укажите оплаченный урок (если применим)",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        obj = self.course_paid if self.course_paid else self.single_lesson_paid
        return f"Платеж {self.id}: {self.user.email} - {self.amount} руб. ({obj})"
