from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="admin@sky.pro")
        self.course = Course.objects.create(
            name="Курс 1", description="Описание курса 1", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Урок 1.1", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        """Тест детального просмотра урока владельцем."""
        url = reverse("materials:lesson-retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)

    def test_lesson_create(self):
        """Тест успешного создания урока авторизованным пользователем."""
        url = reverse("materials:lesson-create")
        data = {"name": "Урок 1-2", "course": self.course.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        """Тест частичного обновления урока его владельцем."""
        url = reverse("materials:lesson-update", args=(self.lesson.pk,))
        data = {"name": "Урок 1.2"}
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Урок 1.2")

    def test_lesson_delete(self):
        """Тест удаления урока его владельцем."""
        url = reverse("materials:lesson-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        """Тест вывода списка уроков."""
        url = reverse("materials:lesson-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "video_url": None,
                    "name": self.lesson.name,
                    "description": self.lesson.description,
                    "preview": None,
                    "course": self.course.pk,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_lesson_create_by_moder_denied(self):
        from django.contrib.auth.models import Group

        moder_group, _ = Group.objects.get_or_create(name="Модераторы")
        moder_user = User.objects.create(email="moder@sky.pro")
        moder_user.groups.add(moder_group)

        self.client.force_authenticate(user=moder_user)

        url = reverse("materials:lesson-create")
        data = {"name": "Урок Модератора", "course": self.course.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve_by_not_owner_denied(self):
        """Тест детального просмотра урока не владельцем."""
        url = reverse("materials:lesson-retrieve", args=(self.lesson.pk,))
        any_user = User.objects.create(email="user@sky.pro")
        self.client.force_authenticate(user=any_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="admin@sky.pro")
        self.course = Course.objects.create(
            name="Курс 1", description="Описание курса 1", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Урок 1.1", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        """Тест детального просмотра курса владельцем."""
        url = reverse("materials:courses-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.course.name)

    def test_course_create(self):
        """Тест успешного создания курса авторизованным пользователем."""
        url = reverse("materials:courses-list")
        data = {
            "name": "Курс 2.0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

    def test_course_update(self):
        """Тест частичного обновления курса его владельцем."""
        url = reverse("materials:courses-detail", args=(self.course.pk,))
        data = {"name": "Курс 2"}
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Курс 2")

    def test_course_delete(self):
        """Тест удаления курса его владельцем."""
        url = reverse("materials:courses-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)

    def test_course_list(self):
        """Тест вывода списка курсов."""
        url = reverse("materials:courses-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.course.pk,
                    "name": self.course.name,
                    "owner": self.user.pk,
                    "description": self.course.description,
                    "lessons_count": 1,
                    "lessons": [
                        {
                            "id": self.lesson.pk,
                            "video_url": None,
                            "name": self.lesson.name,
                            "description": None,
                            "preview": None,
                            "course": self.course.pk,
                            "owner": self.user.pk,
                        }
                    ],
                    "is_subscribed": False,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class SubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="admin@sky.pro")
        self.course = Course.objects.create(
            name="Курс 1", description="Описание курса 1", owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("materials:course-subscribe")

    def test_subscription_add(self):
        """Тест успешного добавления подписки."""
        data = {"course_id": self.course.pk}
        response = self.client.post(self.url, data=data)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("message"), "Подписка успешно добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_remove(self):
        """Тест успешного удаления подписки (повторное нажатие)."""
        Subscription.objects.create(user=self.user, course=self.course)

        data = {"course_id": self.course.pk}
        response = self.client.post(self.url, data=data)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("message"), "Подписка успешно удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )
