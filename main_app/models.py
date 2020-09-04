from django.db import models
from django.conf import settings # Don't refer to the user model directly, it is recommended to refer to the AUTH_USER_MODEL setting
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db.models import Q
from model_utils import FieldTracker
from django.urls import reverse
from decimal import Decimal

# ────────────────────────────────────────────────────────────────────────────────

class TimeStampMixin(models.Model):
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='Date Modified')

  class Meta:
    abstract = True

# ────────────────────────────────────────────────────────────────────────────────

class Cart(TimeStampMixin):
  class Status(models.IntegerChoices):
    CURRENT = 1
    ABANDONED = -1
    IN_PROGRESS = 2
    CANCELLED = -2
    FULFILLED = 3

  status_help_text = """
    <br/>
    A Cart can be in 1 of 5 states:<br/>
    🛒 <strong>Current</strong> - The currently open cart (each user can only have 1 cart in this state)<br/>
    ⏳ <strong>In progress</strong> - Cart has been submitted but not yet fulfilled or cancelled<br/>
    ✅ <strong>Fulfilled</strong> - Items have been delivered to client and payment has been received<br/>
    ❌ <strong>Cancelled</strong> - Cart can no longer be fulfilled<br/>
    🚧 <strong>Abandoned</strong> - The last item in the cart was removed (this will occur automatically)<br/>
  
  """
  
  discount_percent_applied_help_text = """
    Defaults to using the User's discount percent<br/>
  """

  tax_percent_help_text = """
    Defaults to using the User's tax percent<br/>
  """

  closed_at_help_text = """
    Date when the cart was last marked as <strong>Fulfilled</strong>, <strong>Cancelled</strong>, or <strong>Abandoned</strong>
  """

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 1:M, a user can have many carts
  status = models.IntegerField(choices=Status.choices, help_text=status_help_text)
  discount_percent_applied = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    blank=True,
    validators=[MinValueValidator(0), MaxValueValidator(100),],
    verbose_name='Discount (%)',
    help_text=discount_percent_applied_help_text
  )
  tax_percent_applied = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    blank=True,
    validators=[MinValueValidator(0), MaxValueValidator(100),],
    verbose_name='Tax (%)',
    help_text=tax_percent_help_text
  )
  ordered_at = models.DateTimeField(null=True, blank=True, verbose_name='Date Ordered')
  closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Date Closed', help_text=closed_at_help_text)

  def __str__(self):
    return f'Cart #{self.id}'
    
  # @property
  # def get_total(self):
  #   return self.cartDetail_set.all().count()
  
  # discount_percent_applied and tax_percent_applied default values are pulled from the User when one is not explicitly entered
  def save(self, *args, **kwargs):
    if not self.discount_percent_applied:
      self.discount_percent_applied = self.user.discount_percent
    if not self.tax_percent_applied:
      self.tax_percent_applied = self.user.tax_percent
    super(Cart, self).save(*args, **kwargs)

# @receiver(pre_save, sender=Cart)
# def get_user_discount_ratio(sender, instance, *args, **kwargs):
#     instance.discount_ratio = instance.user.discount_ratio

  def get_subtotal(self):
    cart = Cart.objects.get(pk=self.pk)
    subtotal = Decimal('0.00') # Need to use Decimal type so that 0 is displayed as 0.00
    for cartDetail in self.cartdetail_set.all():
      subtotal += cartDetail.quantity * cartDetail.tire.price
    return subtotal
  get_subtotal.short_description = 'Subtotal ($)'

  def get_discount_amount(self):
    return round(self.get_subtotal() * self.discount_percent_applied / 100, 2)
  get_discount_amount.short_description = 'Discount amount ($)'

  def get_tax_amount(self):
    return round(self.get_subtotal() * self.tax_percent_applied / 100, 2)
  get_tax_amount.short_description = 'Tax amount ($)'
  
  def get_total(self):
    return self.get_subtotal() - self.get_discount_amount() + self.get_tax_amount()
  get_total.short_description = 'Total ($)'

  def get_owner(self):
    return self.user.full_name
  get_owner.short_description = 'Full name'
    
  def get_item_count(self):
    cart = Cart.objects.get(id=self.id)
    count = 0
    for cartDetail in cart.cartdetail_set.all():
      count += cartDetail.quantity
    return count
  get_item_count.short_description = 'Number of items'

  status_tracker = FieldTracker(fields=['status'])

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['user','status'], condition=Q(status=1), name='unique_current_cart')
    ]

  @staticmethod
  def does_state_require_shipping_info(status):
    if (status == Cart.Status.IN_PROGRESS or status == Cart.Status.FULFILLED or status == Cart.Status.CANCELLED):
      return True

  def get_order_number(self):
    order_number = self.ordershipping.pk
    return order_number
  get_order_number.short_description = 'Order #'

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
  load_speed = models.CharField(max_length=30, blank=True, verbose_name='Load Index / Speed Rating')
  
  price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Price ($)')
  sale_price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Sale Price ($)')
  image = models.CharField(max_length=200, blank=True, verbose_name='Tire photo URL')
  current_quantity = models.PositiveIntegerField(default=0)
  sold = models.PositiveIntegerField(default=0)

  def __str__(self):
    return self.name

  def get_total_quantity(self):
    return self.current_quantity + self.sold
  get_total_quantity.short_description = 'Total'

  # When a Tire instance is saved, update the price_each on Cart_Detail objects that reference that tire
  def save(self, *args, **kwargs):
    cartDetails = self.cartdetail_set.filter(cart__status=0)
    for cd in cartDetails:
      cd.price_each = self.price
      cd.save()
    super(Tire, self).save(*args, **kwargs)

  def get_absolute_url(self):
    return reverse('tire_detail', args=[str(self.id)])

# ────────────────────────────────────────────────────────────────────────────────

class CartDetail(TimeStampMixin):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
  tire = models.ForeignKey(Tire, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)
  price_each = models.DecimalField(max_digits=7, decimal_places=2, blank=True, verbose_name='Price per item ($)')
  
  def __str__(self):
    return f'{self.cart} –  {self.tire} - QTY: {self.quantity}'

  def get_subtotal(self):
    return self.quantity * self.tire.price
  get_subtotal.short_description = 'Subtotal ($)'

  class Meta:
    verbose_name = 'Cart Item'
    constraints = [
      models.UniqueConstraint(fields=['cart', 'tire'], name='unique_tire_per_cart')
    ]

  # When saving for the first time, use the Tire's price
  def save(self, *args, **kwargs):
    if not self.price_each:
      self.price_each = self.tire.price
    super(CartDetail, self).save(*args, **kwargs)
    if self.quantity == 0:
      self.delete()

# ────────────────────────────────────────────────────────────────────────────────

class OrderShipping(models.Model):
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

  address_help_text = """
    Street address, P.O. box, c/o.
  """

  address_2_help_text = """
    Apartment, suite, unit, building, floor, etc.
  """

  cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  company_name = models.CharField(max_length=50, blank=True, verbose_name='Company')
  business_phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
  country_iso = models.CharField(max_length=3, choices=COUNTRY_CHOICES, default=COUNTRY_CHOICES[0][0], verbose_name='Country')
  province_iso = models.CharField(max_length=2, choices=PROVINCE_CHOICES, default=PROVINCE_CHOICES[8][0], verbose_name='Province')
  city = models.CharField(max_length=30)
  address = models.CharField(max_length=30, verbose_name='Address', help_text=address_help_text)
  address_2 = models.CharField(max_length=30, blank=True, verbose_name='Address Line 2 (optional)', help_text=address_2_help_text)
  postal_code = models.CharField(max_length=30, blank=True)
  gst_number = models.CharField(validators=[MinLengthValidator(15)], max_length=15, blank=True, verbose_name='GST/HST #')

  def __str__(self):
    return f'Order # {self.pk}'

  class Meta:
    verbose_name = 'Shipping Info'
    verbose_name_plural = 'Shipping Info'