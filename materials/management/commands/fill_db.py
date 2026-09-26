from decimal import Decimal

from django.core.management import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    """
    Кастомная команда для наполнения базы данных тестовыми данными.
    """

    help = "Добавляет тестовые данные (пользователи, уроки, курсы, платежи) в БД"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Очистка старых данных..."))
        Payment.objects.all().delete()
        Lesson.objects.all().delete()
        Course.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Старые данные успешно удалены."))
        self.stdout.write(self.style.WARNING("Создание новых тестовых данных..."))

        users_list = []
        for i in range(1, 5):
            user = User(
                email=f"user{i}@example.com",
                first_name=f"Имя_{i}",
                last_name=f"Фамилия_{i}",
                city="Москва",
                phone_number=f"+7999111222{i}",
            )
            user.set_password("testpass123")
            user.save()
            users_list.append(user)
        self.stdout.write(f"- Создано пользователей: {len(users_list)}.")

        courses = [
            {
                "name": "Python-разработчик",
                "description": "Полный курс по разработке на Python и Django.",
            },
            {
                "name": "Frontend-разработчик",
                "description": "Курс по HTML, CSS, JavaScript и React.",
            },
        ]
        courses_list = []
        for c_data in courses:
            course = Course.objects.create(**c_data)
            courses_list.append(course)
        self.stdout.write(f"- Создано курсов: {len(courses_list)}.")

        lessons = [
            {
                "name": "Основы синтаксиса Python",
                "description": "Переменные, циклы и типы данных.",
                "course": courses_list[0],
            },
            {
                "name": "Введение в Django ORM",
                "description": "Работа с моделями и базами данных.",
                "course": courses_list[0],
            },
            {
                "name": "Верстка на Flexbox",
                "description": "Современные методы выравнивания элементов.",
                "course": courses_list[1],
            },
        ]
        lessons_list = []
        for l_data in lessons:
            lesson = Lesson.objects.create(**l_data)
            lessons_list.append(lesson)
        self.stdout.write(f"- Создано уроков: {len(lessons_list)}.")

        # Платеж 1: Оплата всего курса 1 пользователем 1 (перевод)
        Payment.objects.create(
            user=users_list[0],
            amount=Decimal("150000.00"),
            payment_method="bank_transfer",
            course_paid=courses_list[0],
        )
        # Платеж 2: Оплата отдельного урока пользователем 2 (наличные)
        Payment.objects.create(
            user=users_list[1],
            amount=Decimal("15000.00"),
            payment_method="cash",
            single_lesson_paid=lessons_list[0],
        )
        # Платеж 3: Оплата всего курса пользователем 3 (наличные)
        Payment.objects.create(
            user=users_list[2],
            amount=Decimal("120000.00"),
            payment_method="cash",
            course_paid=courses_list[1],
        )
        # Платеж 4: Оплата отдельного урока пользователем 4 (перевод)
        Payment.objects.create(
            user=users_list[3],
            amount=Decimal("1200.00"),
            payment_method="bank_transfer",
            single_lesson_paid=lessons_list[1],
        )
        self.stdout.write("- Создано платежей: 4")

        self.stdout.write(
            self.style.SUCCESS("База данных успешно заполнена тестовыми данными!")
        )
