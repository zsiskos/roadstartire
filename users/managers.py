from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

"""
If your user model defines fields different from Django's default user, you must define a custom manager that extends BaseUserManager, 
providing two additional methods: create_user and create_superuser
"""

# Custom user model manager where email is the unique identifier for authentication instead of usernames
class CustomUserManager(BaseUserManager):
  # Create and save a User with the given email and password
  def create_user(self, email, password, **extra_fields):
    if not email:
      raise ValueError(_('The Email must be set'))
    email = self.normalize_email(email) # Normalizes email addresses by lowercasing the domain portion of the email address.
    user = self.model(email=email, **extra_fields)
    user.set_password(password) 
    user.save()
    return user

  # Create and save a SuperUser with the given email and password
  def create_superuser(self, email, password, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_active', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError(_('Superuser must have is_staff=True.'))
    if extra_fields.get('is_superuser') is not True:
      raise ValueError(_('Superuser must have is_superuser=True.'))
    return self.create_user(email, password, **extra_fields)