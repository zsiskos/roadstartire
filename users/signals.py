from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser
from django.core.mail import send_mail

# After a user is verified (ie. after a CustomUser.is_active is set to True), send them an email
@receiver(pre_save, sender=CustomUser)
def send_verification_email(sender, instance, *args, **kwargs):
  if CustomUser.objects.filter(pk=instance.pk).exists() and instance.is_active != CustomUser.objects.get(id=instance.id).is_active:
    if instance.is_active: # User was marked as active
      email = instance.email
      subject = f"Your Roadstar Tire Wholesale account was successfully verified"
      message = f"Hello {instance.full_name} – We are happy to inform you that your Roadstar Tire Wholesale account was successfully verified.\nAs a verified user, you have access to our wide selection of tires on our website.\n\nLog in: {instance.email}"
      send_mail(
        subject, 
        message, 
        'settings.EMAIL_HOST_USER', 
        [email], 
        fail_silently=False
      )
    else: # User was marked as inactive
      email = instance.email
      subject = f"Your Roadstar Tire Wholesale account is inactive"
      message = f"Hello {instance.full_name} – This is an email confirmation to inform you that your Roadstar Tire Wholesale account was recently inactvated.\nYou will be unable to log in until a staff member verifies your account again."
      send_mail(
        subject, 
        message, 
        'settings.EMAIL_HOST_USER', 
        [email], 
        fail_silently=False
      )