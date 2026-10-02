from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.views import (PaymentListAPIView, PaymentStripeCreateAPIView,
                         PaymentStripeStatusRetrieveAPIView, UserViewSet)

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment_list"),
    path(
        "payments/stripe/",
        PaymentStripeCreateAPIView.as_view(),
        name="payment_stripe_create",
    ),
    path(
        "payments/<int:pk>/status/",
        PaymentStripeStatusRetrieveAPIView.as_view(),
        name="payment_stripe_status",
    ),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
]

urlpatterns += router.urls
