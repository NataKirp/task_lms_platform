from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "get_groups",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "city")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email",)

    # Переопределяем порядок блоков на форме редактирования:
    fieldsets = (
        # Блок 1: Главное
        ("Учетные данные", {"fields": ("email", "password")}),
        # Блок 2: Личная информация
        (
            "Персональные данные",
            {"fields": ("first_name", "last_name", "avatar", "phone_number", "city")},
        ),
        # Блок 3: Права (Группы и статусы)
        (
            "Права и статусы",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        # Блок 4: Системные даты и токены
        ("Служебная информация", {"fields": ("last_login", "date_joined")}),
    )

    # Метод, который будет генерировать текст для ячейки
    @admin.display(description="Группы")  # Название столбца в админке
    def get_groups(self, obj):
        # obj — это текущий пользователь в строке таблицы.
        # Собираем все имена его групп в одну строчку через запятую
        groups_list = [group.name for group in obj.groups.all()]

        if groups_list:
            return ", ".join(groups_list)
        return "-"  # Выводим прочерк, если пользователь не состоит в группах

    # Метод для безопасного хеширования пароля при сохранении через админку
    def save_model(self, request, obj, form, change):
        # Если это создание нового пользователя или пароль был изменен вручную в админке
        if "password" in form.changed_data:
            obj.set_password(obj.password)  # Хешируем текстовый пароль из формы

        super().save_model(request, obj, form, change)
