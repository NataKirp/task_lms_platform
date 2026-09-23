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


class UserProfileSerializer(ModelSerializer):
    """
    Сериализатор для СВОЕГО профиля (Доп. задание №2).
    Включает полную информацию, фамилию и историю платежей.
    """

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
        ]


class UserReadOnlySerializer(ModelSerializer):
    """
    Сериализатор для ЧУЖОГО профиля (Доп. задание №3).
    Скрывает пароль, фамилию и историю платежей. Доступна только общая информация.
    """

    class Meta:
        model = User
        fields = ["id", "email", "city"]


class PaymentSerializer(ModelSerializer):
    """
    Сериализатор для модели платежей.

    Выводит полную информацию о совершенных транзакциях.
    """

    class Meta:
        model = Payment
        fields = "__all__"
