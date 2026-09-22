import getpass

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создает суперпользователя"
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('--- Создание суперпользователя ---'))

        email = input('Email: ').strip()
        # скрываем вводимые символы в терминале
        password = getpass.getpass('Пароль: ')

        if not email:
            self.stdout.write(self.style.ERROR('Ошибка: Email не может быть пустым!'))
            return

        try:
            user = User.objects.create(email=email)
            user.set_password(password)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(self.style.SUCCESS(f'Суперпользователь {user.email} успешно создан!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка при создании: {e}'))