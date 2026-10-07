import stripe
from django.shortcuts import get_object_or_404

from config.settings import STRIPE_API_KEY
from materials.models import Course
from users.models import Payment

stripe.api_key = STRIPE_API_KEY


def get_or_create_stripe_price(obj):
    """
    Принимает объект курса.
    Проверяет, создан ли продукт, совпадает ли цена, и возвращает stripe_price_id.
    """
    # Если продукта еще нет в Stripe, создаем его
    if not obj.stripe_product_id:
        stripe_product = stripe.Product.create(name=obj.name)
        obj.stripe_product_id = stripe_product.id
        obj.save()

    # Запрашиваем цену из Stripe, если совпадает с ценой в бд - возвращаем существующий ID,
    # иначе переходим к созданию цены
    if obj.stripe_price_id:
        try:
            current_stripe_price = stripe.Price.retrieve(obj.stripe_price_id)
            database_price = int(obj.price * 100)
            if current_stripe_price.unit_amount == database_price:
                return obj.stripe_price_id
        except stripe.error.StripeError:
            pass

    new_stripe_price = stripe.Price.create(
        currency="rub", unit_amount=int(obj.price * 100), product=obj.stripe_product_id
    )
    obj.stripe_price_id = new_stripe_price.id
    obj.save()

    return obj.stripe_price_id


def create_stripe_session(user, course_id):
    """Создает сессию на оплату курса в страйпе."""
    # Получаем объект курса по ID
    course_item = get_object_or_404(Course, id=course_id)
    # Формируем цену в Stripe для объекта курса
    stripe_price_id = get_or_create_stripe_price(course_item)
    stripe_session = stripe.checkout.Session.create(
        line_items=[{"price": stripe_price_id, "quantity": 1}],
        mode="payment",
        success_url="http://127.0.0.1:8000/",
        cancel_url="http://127.0.0.1:8000/",
    )

    payment = Payment.objects.create(
        user=user,
        amount=course_item.price,
        payment_method="stripe",
        stripe_session_id=stripe_session.id,
        stripe_link=stripe_session.url,
        status="pending",
        course_paid=course_item,
        single_lesson_paid=None,
    )

    return payment


def check_stripe_payment_status(stripe_session_id):
    """
    Запрашивает у Stripe актуальный статус сессии оплаты.
    Возвращает статус платежа ('paid' или 'unpaid').
    """
    try:
        session = stripe.checkout.Session.retrieve(stripe_session_id)
        if session.payment_status == "paid":
            return "completed"
        return "pending"
    except stripe.error.StripeError:
        return "pending"
