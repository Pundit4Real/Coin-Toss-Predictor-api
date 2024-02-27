from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    A signal handler that creates a new auth token for every newly created user.
    """
    if created:
        Token.objects.create(user=instance)


# # This signal handler function is triggered when a password reset token is created
# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
#     """
#     Handles password reset tokens
#     When a token is created, an email needs to be sent to the user
#     :param sender: View Class that sent the signal
#     :param instance: View Instance that sent the signal
#     :param reset_password_token: Token Model Object
#     :param args: Additional arguments
#     :param kwargs: Additional keyword arguments
#     :return: None
#     """
#     # Base URL for the application, use 'http://localhost:8000' for local development
#     base_url = "http://localhost:8000"

#     # Construct reset password URL
#     reset_password_url = reverse_lazy(
#         'password_reset:reset-password-request') + '?token={}'.format(reset_password_token.key)

#     # Construct the absolute URL
#     reset_password_absolute_url = base_url.rstrip('/') + str(reset_password_url)

#     # Context to pass to the email template
#     context = {
#         'current_user': reset_password_token.user,
#         'username': reset_password_token.user.username,
#         'email': reset_password_token.user.email,
#         'reset_password_url': reset_password_absolute_url,
#     }

#     # Render email text from email template
#     email_html_message = render_to_string('email/password_reset_email.html', context)
#     email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

#     # Create EmailMultiAlternatives object
#     msg = EmailMultiAlternatives(
#         # Subject of the email
#         "Password Reset for Predict and Win Application",
#         # Plain text version of the email
#         email_plaintext_message,
#         # From email address
#         "noreply@yourdomain.com",
#         # To email addresses
#         [reset_password_token.user.email]
#     )

#     # Attach HTML version of the email
#     msg.attach_alternative(email_html_message, "text/html")

#     # Send the email
#     msg.send()
