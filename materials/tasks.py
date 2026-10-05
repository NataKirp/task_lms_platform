from celery import shared_task
from django.core.mail import send_mail

from django.conf import settings


@shared_task
def send_course_update_email(email, course_name):
    """
    Асинхронная задача рассылки писем об обновлении курса.
    """
    send_mail(
        subject=f"Обновление курса: {course_name}",
        message=f'Здравствуйте! В программе курса "{course_name}" произошли важные изменения. Зайдите на платформу, чтобы ознакомиться с новыми материалами.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
