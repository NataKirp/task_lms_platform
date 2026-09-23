from rest_framework import permissions
from rest_framework.decorators import permission_classes


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


class IsAccountOwner(permissions.BasePermission):
    """
    Разрешает доступ к редактированию и удалению только владельцу
    этого профиля (аккаунта).
    """

    message = "Вы не можете изменять или удалять чужой профиль."

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and obj == request.user
