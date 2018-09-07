from django.core.mail import send_mail
from device_activity.celery import app


@app.task
def send_invite_email(domain, email, token):
    send_mail(
        'Reserve time',
        'http://{}/account/registration/?token={}'.format(domain, token),
        'admin@reserve.com',
        [email],
        fail_silently=False,
    )
