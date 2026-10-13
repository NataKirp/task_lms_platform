from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from rest_framework.authtoken.admin import User


@shared_task
def deactivate_user():
    """
    Периодическая задача для блокировки пользователей, которые не заходили в систему более 30 дней
    ИЛИ зарегистрировались более 30 дней назад и ни разу не входили.
    """
    today = timezone.now()
    block_date = today - timedelta(days=30)
    inactive_users = User.objects.filter(
        Q(is_active=True, is_superuser=False),
        Q(last_login__lt=block_date)
        | Q(last_login__isnull=True, date_joined__lt=block_date),
    ).distinct()

    for user in inactive_users:
        user.is_active = False
        user.save()

    print(
        f"Автоматическая проверка завершена. Деактивировано пользователей: {inactive_users.count()}"
    )
