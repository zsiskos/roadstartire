from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.contrib.postgres.fields import CIEmailField
from model_utils import FieldTracker
from main_app.models import Cart
import pytz
from timezone_field import TimeZoneField

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

  is_active_help_text = """
    Designates whether this user account should be considered active.<br/>
    <strong>NOTE:</strong> Only active users can log in.
  """
  is_staff_help_text = """
    Designates whether this user can access the admin site.
  """
  discount_percent_help_text = """
    • Discount applied to orders (before tax)<br/>
    • Must be a number from 0.00 to 100.00 (up to 2 decimal places)
  """
  tax_percent_help_text = """
    Tax percentage applied to orders (defaults to <strong>13%</strong>)
  """

  address_help_text = """
    Street address, P.O. box, c/o.
  """

  address_2_help_text = """
    Apartment, suite, unit, building, floor, etc.
  """

  email = CIEmailField(unique=True)
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  is_active = models.BooleanField(default=False, help_text=is_active_help_text)
  is_staff = models.BooleanField(default=False, help_text=is_staff_help_text)
  date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Date Joined')
  company_name = models.CharField(max_length=50, blank=True, verbose_name='Company')
  business_phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
  country_iso = models.CharField(max_length=3, choices=COUNTRY_CHOICES, default=COUNTRY_CHOICES[0][0], verbose_name='Country')
  province_iso = models.CharField(max_length=2, choices=PROVINCE_CHOICES, default=PROVINCE_CHOICES[8][0], verbose_name='Province')
  city = models.CharField(max_length=30, blank=True, verbose_name='City')
  address = models.CharField(max_length=30, verbose_name='Address', help_text=address_help_text)
  address_2 = models.CharField(max_length=30, blank=True, verbose_name='Address Line 2 (optional)', help_text=address_2_help_text)
  postal_code = models.CharField(max_length=30, blank=True)
  gst_number = models.CharField(validators=[MinLengthValidator(15)], max_length=15, blank=True, verbose_name='GST/HST Number')
  discount_percent = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=0,
    verbose_name='Discount (%)',
    validators=[MinValueValidator(0), MaxValueValidator(100),],
    help_text=discount_percent_help_text
  )
  tax_percent = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=13,
    verbose_name='Tax (%)', 
    validators=[MinValueValidator(0), MaxValueValidator(100),], 
    help_text=tax_percent_help_text
  )
  timezone = TimeZoneField(default='America/Toronto')

  # is_active_status_tracker = FieldTracker(fields=['is_active'])
  tax_percent_tracker = FieldTracker(fields=['tax_percent'])
  discount_percent_tracker = FieldTracker(fields=['discount_percent'])

  class Meta:
    # Change model name in admin interface
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  # A string describing the name of the field on the user model that is used as the unique identifier
  USERNAME_FIELD = 'email'
  # A list of the field names that will be prompted for when creating a user via the createsuperuser management command
  REQUIRED_FIELDS = ('first_name', 'last_name',)

  objects = CustomUserManager()

  def __str__(self):
    return self.email

  @property
  def full_name(self):
    return '%s %s' % (self.first_name, self.last_name)

  # If the User's tax_percent is changed, then update the User's current cart if it exists
  def save(self, *args, **kwargs):
    try:
      currentCart = self.cart_set.get(status=Cart.Status.CURRENT)
      if self.tax_percent_tracker.has_changed('tax_percent'):
        currentCart.tax_percent_applied = self.tax_percent
      if self.discount_percent_tracker.has_changed('discount_percent'):
        currentCart.discount_percent_applied = self.discount_percent
      currentCart.save()
    except Cart.DoesNotExist:
      currentCart = None
    super(CustomUser, self).save(*args, **kwargs)