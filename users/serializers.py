from rest_framework.serializers import ModelSerializer

from users.models import Payment


class PaymentSerializer(ModelSerializer):
    """
    Сериализатор для модели платежей.

    Выводит полную информацию о совершенных транзакциях.
    """

    class Meta:
        model = Payment
        fields = "__all__"