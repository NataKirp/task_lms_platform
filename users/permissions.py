from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    message = "Доступ запрещен. Вы не являетесь модератором."

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsNotModer(permissions.BasePermission):
    """Разрешает доступ только тем, кто НЕ является модератором."""

    message = "Модераторам запрещено выполнять это действие."

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Если пользователь в группе Модераторы — возвращаем False (отказ в доступе)
            return not request.user.groups.filter(name="Модераторы").exists()
        return False


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    message = "Доступ запрещен. Вы не являетесь владельцем этого материала."

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
