from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

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
  COUNTRY_CHOICES = [
    ('CAN', 'Canada'),
    ('USA', 'United States')
  ]

  PROVINCE_CHOICES = [
    ('AB', 'Alberta'),
    ('BC', 'British Columbia'),
    ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'),
    ('NL', 'Newfoundland and Labrador'),
    ('NS','Nova Scotia'),
    ('NT', 'Northwest Territories'),
    ('NU', 'Nunavut'),
    ('ON', 'Ontario'), # Default
    ('PE','Prince Edward Island'),
    ('QC', 'Quebec'),
    ('SK', 'Saskatchewan'),
    ('YT', 'Yukon'),
  ]

  email = models.EmailField(unique=True)
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  is_active = models.BooleanField(default=True, help_text='Designates whether this user account should be considered active.<br/><strong>NOTE:</strong> Recommended that you set this flag to False instead of deleting accounts; that way, if any applications store foreign keys to users, the foreign keys won’t break.')
  is_staff = models.BooleanField(default=False, help_text='Designates whether this user can access the admin site.')
  date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Date Joined (UTC)')
  company_name = models.CharField(max_length=50, blank=True, verbose_name='Company')
  business_phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
  country_iso = models.CharField(max_length=3, choices=COUNTRY_CHOICES, default=COUNTRY_CHOICES[0][0], verbose_name='Country')
  province_iso = models.CharField(max_length=2, choices=PROVINCE_CHOICES, default=PROVINCE_CHOICES[8][0], verbose_name='Province')
  city = models.CharField(max_length=30, blank=True)
  address = models.CharField(max_length=30, blank=True)
  postal_code = models.CharField(max_length=30, blank=True)
  hst_number = models.CharField(max_length=30, blank=True, verbose_name='HST Number')
  discount_ratio = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Discount', validators=[MinValueValidator(0), MaxValueValidator(1)], help_text='Must be a number from 0.00 to 1.00 (up to 2 decimal places)')

  class Meta:
    # Change model name in admin interface
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  
  # A string describing the name of the field on the user model that is used as the unique identifier
  USERNAME_FIELD = 'email'
  # A list of the field names that will be prompted for when creating a user via the createsuperuser management command
  REQUIRED_FIELDS = ['first_name', 'last_name',]

  objects = CustomUserManager()

  def __str__(self):
    return self.email