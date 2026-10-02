from django.contrib import admin

from materials.models import Course, Lesson, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Настройка отображения курсов в админ-панели.
    """

    # Поля, которые будут отображаться в списке всех курсов
    list_display = ("id", "name", "price", "owner")
    # Поля, по которым можно кликнуть для перехода внутрь курса
    list_display_links = ("id", "name")
    # Поля, по которым доступен быстрый поиск
    search_fields = ("name", "description")
    # Системные поля Stripe делаем только для чтения, чтобы их нельзя было случайно сломать
    readonly_fields = ("stripe_product_id", "stripe_price_id")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Настройка отображения уроков в админ-панели.
    """

    list_display = ("id", "name", "course", "owner")
    list_display_links = ("id", "name")
    list_filter = ("course",)
    search_fields = ("name", "description")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Настройка отображения подписок в админ-панели.
    """

    list_display = ("id", "user", "course")
    list_filter = ("course", "user")
