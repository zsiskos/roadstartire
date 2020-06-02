from django.db import models
from django.conf import settings # Don't refer to the user model directly, it is recommended to refer to the AUTH_USER_MODEL setting
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

# ────────────────────────────────────────────────────────────────────────────────

class Cart(models.Model):
  class Status(models.IntegerChoices):
    CURRENT = 0
    IN_PROGRESS = 1
    CANCELLED = 2
    FULFILLED = 3

  status_help_text = """
    <br/>
    A Cart can be in 1 of 4 states:<br/>
    1. <strong>Current</strong> - The currently open cart (each user can only have 1 cart in this state)<br/>
    2. <strong>In progress</strong> - Cart has been submitted but not yet fulfilled nor cancelled<br/>
    3. <strong>Cancelled</strong> - Cart can no longer be fulfilled<br/>
    4. <strong>Fulfilled</strong> - Items have been delivered to client and payment has been received<br/>
    <br/>
    <strong>NOTE: </strong>A Cart's status must only ever progress forwards
  """
  
  discount_ratio_applied_help_text = """
    • Leave this field blank to use the User's current discount ratio<br/>
    • Must be a number from 0.00 to 1.00 (up to 2 decimal places)
  """

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 1:M, a user can have many carts
  date_ordered = models.DateTimeField(auto_now_add=True, verbose_name='Date Created (UTC)')
  status = models.IntegerField(choices=Status.choices, help_text=status_help_text)
  discount_ratio_applied = models.DecimalField(max_digits=4, decimal_places=2, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1),], help_text=discount_ratio_applied_help_text)

  def get_readable_status(self):
    if self.status == 0:
      return 'Current'
    elif self.status == 1:
      return 'In progress'
    elif self.status == 2:
      return 'Cancelled'
    elif self.status == 4:
      return 'Fulfilled'

  def __str__(self):
    return f'{self.user.first_name} {self.user.last_name} - Cart #{self.id} - {self.get_readable_status()}'
    
  def get_total(self):
    pass
  
  # When saving, use the User's current discount ratio if one is not explicitly entered
  def save(self, *args, **kwargs):
    if not self.discount_ratio_applied:
      self.discount_ratio_applied = self.user.discount_ratio
    super(Cart, self).save(*args, **kwargs)

# @receiver(pre_save, sender=Cart)
# def get_user_discount_ratio(sender, instance, *args, **kwargs):
#     instance.discount_ratio_applied = instance.user.discount_ratio

# ────────────────────────────────────────────────────────────────────────────────

class Tire(models.Model):
  name = models.CharField(max_length=30)
  brand = models.CharField(max_length=30)
  year = models.CharField(max_length=30)
  width = models.CharField(max_length=30, blank=True)
  aspect_ratio = models.CharField(max_length=30, blank=True)
  rim_size = models.CharField(max_length=30, blank=True)
  season = models.CharField(max_length=30, blank=True)
  pattern = models.CharField(max_length=30, blank=True)
  loads = models.CharField(max_length=30, blank=True)
  price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Price ($)')
  image = models.CharField(max_length=200, blank=True, verbose_name='Tire photo URL')
  current_quantity = models.PositiveIntegerField(default=0)
  total_quantity = models.PositiveIntegerField(default=0)
  sold = models.PositiveIntegerField(default=0)

  def __str__(self):
    return self.name

# ────────────────────────────────────────────────────────────────────────────────

class CartDetail(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
  tire = models.ForeignKey(Tire, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)

  @property
  def get_sub_total(self):
    return self.quantity * Tire.price
  
  def __str__(self):
    return f'Cart {self.cart} contains {self.quantity} \'{self.tire}\' tires'