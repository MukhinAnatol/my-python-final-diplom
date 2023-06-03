from django.core.mail import send_mail
from orders.settings import EMAIL_HOST_USER


def send_email(order, user):
    subject = 'Произошло изменение заказа'
    message = f'Ваш заказ {order} был изменен.'
    from_email = EMAIL_HOST_USER

    return send_mail(subject, message, from_email, [user])