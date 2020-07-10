from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser
from django.core.mail import send_mail

# After a user is verified (ie. after a CustomUser's is_active field is set to True), notify the user via email
@receiver(pre_save, sender=CustomUser)
def send_verification_email(sender, instance, *args, **kwargs):
  if CustomUser.objects.filter(pk=instance.pk).exists() and instance.is_active != CustomUser.objects.get(id=instance.id).is_active:
    if instance.is_active: # User was marked as active
      email = instance.email
      subject = f"Your Road Star Wholesale account has been successfully verified"
      message = f"Hello {instance.full_name} – We are glad to inform you that your Road Star Wholesale account (# {instance.pk}) has been successfully verified. \nAs a verified user, you now have access to our wide selection of tires on our website so feel free to start shopping!"
      send_mail(
        subject, 
        message, 
        'settings.EMAIL_HOST_USER', 
        [email], 
        fail_silently=False
      )
    else: # User was marked as inactive
      email = instance.email
      subject = f"Your Road Star Wholesale account was recently disabled"
      message = f"Hello {instance.full_name} – This is an email confirmation to let you know that your Road Star Wholesale account (# {instance.pk}) has been disabled. \nYou will be unable to log in again until and admin verifies your account again."
      send_mail(
        subject, 
        message, 
        'settings.EMAIL_HOST_USER', 
        [email], 
        fail_silently=False
      )