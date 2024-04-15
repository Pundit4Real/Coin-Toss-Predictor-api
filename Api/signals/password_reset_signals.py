from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from Api.models import PasswordResetCode


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Create a PasswordResetCode object for the user
    PasswordResetCode.objects.create(user=reset_password_token.user, code=reset_password_token.key)

    # Send an email to the user
    context = {
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_code': reset_password_token.key,  
    }

    # Render email text
    email_html_message = render_to_string('email/password_reset_email.html', context)
    email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

    msg = EmailMultiAlternatives(
        # Title
        "Password Reset for {title}".format(title="Pundit"),
        # Message
        email_plaintext_message,
        # From
        "noreply@yourdomain.com",
        # To
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()

@receiver(post_save, sender=PasswordResetCode)
def mark_code_as_expired(sender, instance, created, **kwargs):
    if created:
        # If the instance is newly created, set the expiration time
        expiration_time = instance.created_at + timezone.timedelta(seconds=120)
        # Check if the current time exceeds the expiration time
        if timezone.now() >= expiration_time:
            instance.is_expired = True
            instance.save()
        else:
            # Schedule the expiration for the future
            from threading import Timer
            time_difference_seconds = (expiration_time - timezone.now()).total_seconds()
            timer = Timer(time_difference_seconds, expire_code, args=[instance.pk])
            timer.start()

def expire_code(code_pk):
    try:
        code = PasswordResetCode.objects.get(pk=code_pk)
        # Check if the code is still not expired (race condition)
        if not code.is_expired:
            code.is_expired = True
            code.save()
    except PasswordResetCode.DoesNotExist:
        pass  # Handle the case where the code has been deleted before expiration