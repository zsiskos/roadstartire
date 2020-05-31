from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager

"""
https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#extending-the-existing-user-model

1. Subclass AbstractBaseUser (as opposed to just AbstractUser) in order to add new fields
  - AbstractBaseUser provides the core implementation of a user model, including hashed passwords and tokenized password resets
2. Add desired fields
3. Set the USERNAME_FIELD -- which defines the unique identifier for the User model -- to email
4. Specifiy that all objects for the class come from the CustomUserManager
"""

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # A string describing the name of the field on the user model that is used as the unique identifier
    USERNAME_FIELD = 'email'
    # A list of the field names that will be prompted for when creating a user via the createsuperuser management command
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
      return self.email