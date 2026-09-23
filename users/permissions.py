from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором или суперпользователем."""

    message = "Доступ запрещен. Вы не являетесь модератором."

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return request.user.groups.filter(name="Модераторы").exists()
        return False


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем или суперпользователем."""

    message = "Доступ запрещен. Вы не являетесь владельцем этого материала."

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return obj.owner == request.user
        return False
