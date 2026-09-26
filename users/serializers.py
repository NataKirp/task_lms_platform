from rest_framework.serializers import ModelSerializer

from users.models import Payment, User


class UserRegisterSerializer(ModelSerializer):
    """
    Сериализатор для РЕГИСТРАЦИИ пользователя.
    """

    class Meta:
        model = User
        fields = ["email", "password", "phone_number", "city"]
        extra_kwargs = {
            "password": {"write_only": True}
        }  # Пароль будет приниматься, но не будет отдаваться в JSON

    def create(self, validated_data):
        password = validated_data.pop(
            "password"
        )  # Извлекаем пароль из валидированных данных
        user = User(
            **validated_data
        )  # Создаем пользователя со всеми оставшимися полями
        user.set_password(password)  # Хэшируем и сохраняем пароль
        user.save()
        return user


class PaymentSerializer(ModelSerializer):
    """
    Сериализатор для модели платежей.

    Выводит полную информацию о совершенных транзакциях.
    """

    class Meta:
        model = Payment
        fields = "__all__"


class UserProfileSerializer(ModelSerializer):
    """
    Сериализатор для СВОЕГО профиля.
    Включает полную информацию, фамилию и историю платежей.
    """

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "city",
            "avatar",
            "payments"
        ]


class UserReadOnlySerializer(ModelSerializer):
    """
    Сериализатор для ЧУЖОГО профиля.
    Скрывает пароль, фамилию и историю платежей. Доступна только общая информация.
    """

    class Meta:
        model = User
        fields = ["id", "email", "city"]
