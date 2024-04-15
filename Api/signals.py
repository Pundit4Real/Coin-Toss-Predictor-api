from django.contrib.auth import get_user_model
from .models import UserProfile,PasswordResetCode
# from django.urls import reverse
from django.db.models.signals import post_save


from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string

from django_rest_passwordreset.signals import reset_password_token_created

User = get_user_model()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Create a PasswordResetCode object for the user
    PasswordResetCode.objects.create(user=reset_password_token.user, code=reset_password_token.key)

    # Send an email to the user
    context = {
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_code': reset_password_token.key,  # Use the reset token key as the reset code
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




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a UserProfile instance when a new User is created.
    """
    if created and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the UserProfile instance whenever the associated User is saved.
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, **kwargs):
    """
    Signal handler to update the UserProfile whenever the associated User is updated.
    """
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    profile.full_name = instance.full_name
    profile.username = instance.username
    profile.save()


@receiver(post_save, sender=UserProfile)
def update_user_balance(sender, instance, **kwargs):
    if kwargs.get('created', False) or instance.balance != instance.user.balance:
        instance.user.balance = instance.balance
        instance.user.save()

# @receiver(post_save, sender=User)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     """
#     A signal handler that creates a new auth token for every newly created user.
#     """
#     if created:
#         Token.objects.create(user=instance)
