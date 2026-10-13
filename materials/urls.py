from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import (CourseViewSet, LessonCreateAPIView,
                             LessonDestroyAPIView, LessonListAPIView,
                             LessonRetrieveAPIView, LessonUpdateAPIView,
                             SubscriptionAPIView)

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lesson/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-retrieve"),
    path(
        "lesson/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"
    ),
    path(
        "lesson/<int:pk>/delete/",
        LessonDestroyAPIView.as_view(),
        name="lesson-delete",
    ),
    path("course/subscribe/", SubscriptionAPIView.as_view(), name="course-subscribe"),
]
urlpatterns += router.urls
