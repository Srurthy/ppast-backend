from django.db.models import signals
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.dispatch import receiver
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from utils import mailer


UserModel = get_user_model()


@receiver(signals.post_save, sender=UserModel)
def send_confirmation_mail(sender, instance, created=False, **kwargs):
    if not created:
        return
    if instance.is_enterprise_admin:

        context = {
            "email": instance.email,
            "uid": urlsafe_base64_encode(force_bytes(instance.pk)),
            "user": instance,
            "full_name": instance.get_full_name(),
            "token": default_token_generator.make_token(instance),
            "domain": getattr(settings, "DOMAIN"),
        }

        subject_template_name = "registration/verify_email_subject.txt"
        email_template_name = "registration/verify_email.txt"
        html_email_template_name = "registration/verify_email.html"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL")
    else:
        context = {
            "email": instance.email,
            "uid": urlsafe_base64_encode(force_bytes(instance.pk)),
            "user": instance,
            "full_name": instance.get_full_name(),
            "token": default_token_generator.make_token(instance),
            "domain": getattr(settings, "DOMAIN"),
        }
        subject_template_name = "registration/password_reset_email_subject.txt"
        email_template_name = "registration/password_reset_email.txt"
        html_email_template_name = "registration/password_reset_email.html"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL")
    mailer.send_mail(
        subject_template_name,
        email_template_name,
        context,
        from_email,
        instance.email,
        html_email_template_name=html_email_template_name,
    )
