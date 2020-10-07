from django.db import models
from django.conf import settings # Don't refer to the user model directly, it is recommended to refer to the AUTH_USER_MODEL setting
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db.models import Q
from model_utils import FieldTracker
from django.urls import reverse
from decimal import Decimal
from django.utils.timezone import now
from django.db.models import Sum
import datetime
from django.utils import timezone
from django.utils.html import format_html

# ────────────────────────────────────────────────────────────────────────────────

class TimeStampMixin(models.Model):
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='Date Modified')

  class Meta:
    abstract = True

# ────────────────────────────────────────────────────────────────────────────────

class Product(models.Model):
  is_archived_help_text = """
    When marked as archived ✔, customers will be unable to view and order this product
  """
  is_archived = models.BooleanField(default=False, verbose_name='Archived', help_text=is_archived_help_text)

  def name(self):
    return self.tire_set.order_by('id').last().name
  name.admin_order_field = 'tire'
  name = property(name)

  @property
  def sold_online_quantity(self):
    sold_online_quantity = 0
    qs = self.cartdetail_set.filter(Q(cart__status=Cart.Status.IN_PROGRESS) | Q(cart__status=Cart.Status.FULFILLED))
    if qs:
      return qs.aggregate(sold_online_quantity=Sum('quantity'))['sold_online_quantity']
    return sold_online_quantity
  sold_online_quantity.fget.short_description = '💰 Sold online'

  @property
  def sold_offline_quantity(self):
    sold_offline_quantity = 0
    qs = self.stock_set.all().filter(quantity_change_type=Stock.SOLD)
    if qs:
      return qs.aggregate(sold_offline_quantity=Sum('quantity_change_value'))['sold_offline_quantity']
    return sold_offline_quantity
  sold_offline_quantity.fget.short_description = '💰 Sold offline'

  @property
  def sold_quantity(self):
    sold_offline_quantity = 0
    sold_online_qs = self.cartdetail_set.filter(Q(cart__status=Cart.Status.IN_PROGRESS) | Q(cart__status=Cart.Status.FULFILLED))
    sold_offline_qs = self.stock_set.all().filter(quantity_change_type=Stock.SOLD)
    if sold_offline_qs:
      sold_offline_quantity = sold_offline_qs.aggregate(sold_offline_quantity=Sum('quantity_change_value'))['sold_offline_quantity']
    if sold_online_qs:
      return sold_online_qs.aggregate(sold_quantity=Sum('quantity') + sold_offline_quantity)['sold_quantity']
    return sold_offline_quantity
  sold_quantity.fget.short_description = '💰 Sold'

  @property
  def shrink_quantity(self):
    shrink_quantity = 0
    qs = self.stock_set.filter(quantity_change_type=Stock.SHRINK)
    if qs:
      shrink_quantity = qs.aggregate(shrink_quantity=Sum('quantity_change_value'))['shrink_quantity']
    return shrink_quantity
  shrink_quantity.fget.short_description = '❓ Lost, damaged, administrative error, etc.'

  @property
  def current_quantity(self):
    current_quantity = 0
    qs = self.stock_set.filter(quantity_change_type=Stock.RECEIVED)
    if qs:
      current_quantity =  qs.aggregate(current_quantity=Sum('quantity_change_value') - self.sold_quantity - self.shrink_quantity)['current_quantity']
    return current_quantity
  current_quantity.fget.short_description = '📦 Current Stock'

  @property
  def total_quantity(self):
    total_quantity = 0
    qs = self.stock_set.filter(quantity_change_type=Stock.RECEIVED)
    if qs:
      total_quantity = qs.aggregate(total_quantity=Sum('quantity_change_value'))['total_quantity']
    return total_quantity
  total_quantity.fget.short_description = 'Total'

  def brand(self):
    return self.get_current().brand
  brand.admin_order_field = 'tire__brand'
  brand = property(brand)

  def year(self):
    return self.get_current().year
  year.admin_order_field = 'tire__year'
  year = property(year)

  def width(self):
    return self.get_current().width
  width.admin_order_field = 'tire__width'
  width = property(width)

  def aspect_ratio(self):
    return self.get_current().aspect_ratio
  aspect_ratio.admin_order_field = 'tire__aspect_ratio'
  aspect_ratio = property(aspect_ratio)

  def rim_size(self):
    return self.get_current().rim_size
  rim_size.admin_order_field = 'tire__rim_size'
  rim_size = property(rim_size)

  def tire_type(self):
    return self.get_current().tire_type
  tire_type.short_description = 'Type'
  tire_type.admin_order_field = 'tire__tire_type'
  tire_type = property(tire_type)

  def pattern(self):
    return self.get_current().pattern
  pattern.admin_order_field = 'tire__pattern'
  pattern = property(pattern)

  def tread(self):
    return self.get_current().tread
  tread.short_description = 'Tread Category'
  tread.admin_order_field = 'tire__tread'
  tread = property(tread)

  def load_speed(self):
    return self.get_current().load_speed
  load_speed.short_description = 'Load Index/Speed Rating'
  load_speed.admin_order_field = 'tire__load_speed'
  load_speed = property(load_speed)
  
  def price(self):
    return self.get_current().price
  price.short_description = 'Price ($)'
  price.admin_order_field = 'tire__price'
  price = property(price)

  def sale_price(self):
    return self.get_current().sale_price
  sale_price.short_description = 'Sale Price ($)'
  sale_price.admin_order_field = 'tire__sale_price'
  sale_price = property(sale_price)

  def __str__(self):
    return self.name

  # def get_current(self):
  #   return self.tire_set.order_by('id').last()

  def get_current(self):
    qs = self.tire_set.filter(date_effective__lte=timezone.now()).order_by('id')
    return qs.last()

  class Meta:
    verbose_name = '⭐️ Product'
    verbose_name_plural = '⭐️ Products'
    
# ────────────────────────────────────────────────────────────────────────────────

class Stock(TimeStampMixin):
  RECEIVED = 'stock received'
  SOLD = 'sold'
  SHRINK = 'shrink'

  CHANGE_TYPE_CHOICES = [
    ('➕ Increase stock', (
        (RECEIVED, '🚚 Stock received'),
      )
    ),
    ('➖ Decrease stock', (
        (SOLD, '💰 ‍Sold offline'),
        (SHRINK, '❓ Lost, damaged, administrative error, etc.'),
      )
    ),
  ]

  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity_change_type = models.CharField(max_length=30, choices=CHANGE_TYPE_CHOICES, default=RECEIVED, verbose_name='Increase/Decrease Stock')
  quantity_change_value = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Quantity')

  def __str__(self):
    return f'{self.quantity_change_value} {self.quantity_change_type}'

  class Meta:
    verbose_name = '🚚 Stock'
    verbose_name_plural = '🚚 Stock'

# ────────────────────────────────────────────────────────────────────────────────

class Tread(models.Model):
  name = models.CharField(max_length=30)

  def __str__(self):
    return self.name

  def get_image_count(self):
    return self.image_set.all().count()
  get_image_count.short_description = 'Total number of images'

  class Meta:
    verbose_name = '📷 Tread Category & Images'
    verbose_name_plural = '📷 Tread Categories & Images'

# ────────────────────────────────────────────────────────────────────────────────

class Image(models.Model):
  tread = models.ForeignKey(Tread, on_delete=models.CASCADE, verbose_name = 'Tread Category')
  url = models.CharField(max_length=200, blank=True, verbose_name='Tire photo URL')

  def __str__(self):
    return f'Image ({self.id}) for {self.tread}'

  def get_image_display(self):
    return format_html("<img style='border: 1px solid lightgray; border-radius: 8px' src={url} width={width} height={height}/>".format(
      url = self.url,
      width = 100, # hardcoded thumbnail dimensions
      height = 100,
      )
    )
  get_image_display.short_description = 'Thumbnail'

  class Meta:
    verbose_name = '📷 Image'
    verbose_name_plural = '📷 Images'

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
  
  # discount_percent_applied and tax_percent_applied default values are pulled from the User when one is not explicitly entered
  def save(self, *args, **kwargs):
    if not self.discount_percent_applied:
      self.discount_percent_applied = self.user.discount_percent
    if not self.tax_percent_applied:
      self.tax_percent_applied = self.user.tax_percent
    super(Cart, self).save(*args, **kwargs)

  def get_subtotal(self):
    subtotal = Decimal('0.00') # Need to use Decimal type so that 0 is displayed as 0.00
    for cartDetail in self.cartdetail_set.all():
      subtotal += cartDetail.quantity * cartDetail.get_relevant_tire().price
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
  
  def get_full_name(self):
    return self.user.full_name
  get_full_name.short_description = 'Full name'
    
  def get_item_count(self):
    return self.cartdetail_set.all().count()
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

  class Meta:
    verbose_name = '🛒 Cart & Order'
    verbose_name_plural = '🛒 Carts & Orders'

# ────────────────────────────────────────────────────────────────────────────────

class Tire(models.Model):
  date_effective_help_text = """
    The date and time when these changes will come into effect
  """

  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  date_effective = models.DateTimeField(default=timezone.now, blank=True, verbose_name='Date Effective', help_text=date_effective_help_text)
  brand = models.CharField(max_length=30)
  year = models.CharField(max_length=30, blank=True)

  width = models.CharField(max_length=30, blank=True)
  aspect_ratio = models.CharField(max_length=30, blank=True)
  rim_size = models.CharField(max_length=30, blank=True)
  tire_type = models.CharField(max_length=30, blank=True, verbose_name='Type')
  pattern = models.CharField(max_length=30, blank=True)
  tread = models.ForeignKey(Tread, null=True, blank=True, on_delete=models.CASCADE, verbose_name = 'Tread Category')
  load_speed = models.CharField(max_length=30, blank=True, verbose_name='Load Index/Speed Rating')
  
  price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Price ($)')
  sale_price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Sale Price ($)')

  date_effective_tracker = FieldTracker(fields=['date_effective'])
  
  def product_num(self):
    return self.product.id
  product_num.short_description = 'Product ID'
  product_num.admin_order_field = 'product__id'
  product_num = property(product_num)

  @property
  def name(self):
    return f'{self.brand} {self.width}/{self.aspect_ratio}{self.rim_size} {self.pattern} {self.load_speed}'

  @property
  def product_number(self):
    return self.product.id

  updated_to = models.OneToOneField('self', null=True, blank=True, on_delete=models.CASCADE, related_name='updated_tire_set')
  inherits_from = models.OneToOneField('self', null=True, blank=True, on_delete=models.CASCADE, related_name='inherits_tire_set')

  def __str__(self):
    return self.name

  # When a Tire instance is saved, update the CartDetail.date_relevant objects that reference that tire
  def save(self, *args, **kwargs):
    cartDetails = self.product.cartdetail_set.filter(cart__status=Cart.Status.CURRENT)
    for cd in cartDetails:
      cd.date_relevant = timezone.now()
      cd.save()
    super(Tire, self).save(*args, **kwargs)

  def get_absolute_url(self):
    return reverse('tire_detail', args=[str(self.id)])

  # Very important function!
  # Retrieves the tire version that was most recently add/updated and is past its effective date
  # Need to order by id (not by date_effective, since they could potentially not be entered in chronological order)
  def get_updated_tire(self):
    qs = Tire.objects.filter(Q(product=self.product) & Q(date_effective__lte=timezone.now())).order_by('id')
    return qs.last()

  # Doesn't take into account the date_effective
  # def get_updated_tire(self):
  #   if self.updated_to:
  #     return self.updated_to.get_updated_tire()
  #   return self

  def get_date_effective_delta(self):
    delta = self.date_effective - timezone.now()
    return Tire.strfdelta(delta, '%s%D %H:%M:%S')
  get_date_effective_delta.short_description = 'Time until tire details are effective'
  
  @property
  def is_effective(self):
    if self.get_updated_tire() == self:
      return True
    else:
      return False
  is_effective.fget.short_description = 'Effective'

  @staticmethod
  def strfdelta(td, fmt):
    # Get the timedelta’s sign and absolute number of seconds.
    sign = "-" if td.days < 0 else "+"
    secs = abs(td).total_seconds()

    # Break the seconds into more readable quantities.
    days, rem = divmod(secs, 86400)  # Seconds per day: 24 * 60 * 60
    hours, rem = divmod(rem, 3600)  # Seconds per hour: 60 * 60
    mins, secs = divmod(rem, 60)

    # Format (as per above answers) and return the result string.
    t = DeltaTemplate(fmt)
    return t.substitute(
        s=sign,
        D="{:d}".format(int(days)),
        H="{:02d}".format(int(hours)),
        M="{:02d}".format(int(mins)),
        S="{:02d}".format(int(secs)),
        )

  class Meta:
    verbose_name = '📜 Tire Details'
    verbose_name_plural = '📜 Tire Details'

from string import Template
class DeltaTemplate(Template):
  delimiter = "%"

# ────────────────────────────────────────────────────────────────────────────────

class CartDetail(TimeStampMixin):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)
  # TODO: Remove price_each field since price is obtained through the Tire model
  price_each = models.DecimalField(max_digits=7, decimal_places=2, blank=True, verbose_name='Price per item ($)')
  date_relevant = models.DateTimeField(default=now, blank=True, verbose_name='Date Relevant') # Need this to know which Tire version to use for invoices
  # TODO: Update the date_relevant field for cartdetails that in a IN_PROGRESS cart every x minutes so that buyers can't hold on to an old reference of a Tire if it's price and other details have been updated

  def __str__(self):
    return f'{self.product.get_current()} - QTY: {self.quantity}'

  def get_subtotal(self):
    return self.quantity * self.get_relevant_tire().price
  get_subtotal.short_description = 'Subtotal ($)'

  class Meta:
    verbose_name = '🛒📦 Cart Item'
    constraints = [
      models.UniqueConstraint(fields=['cart', 'product'], name='unique_product_per_cart'),
    ]

  # When saving for the first time, use the Tire's price
  def save(self, *args, **kwargs):
    if not self.price_each:
      self.price_each = self.product.get_current().price
    super(CartDetail, self).save(*args, **kwargs)
    if self.quantity == 0:
      self.delete()

  def get_relevant_tire(self):
    qs = self.product.tire_set.filter(date_effective__lte=self.date_relevant).order_by('date_effective', 'id')
    return qs.last()

  def get_updated_tire(self):
    qs = self.product.tire_set.filter(date_effective__lte=timezone.now()).order_by('date_effective')
    return qs.last()

  @property
  def price(self):
    return self.get_relevant_tire().price
  price.fget.short_description = 'Price ($)'

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
    return f'Order #{self.pk}'

  # Purely so that on the admin, it reads as Order # and can be sorted as well
  def order_number(self):
    return self.id
  order_number.short_description = 'Order #'
  order_number.admin_order_field = 'id'
  order_number = property(order_number)

  class Meta:
    verbose_name = '📦 Shipping Info'
    verbose_name_plural = '📦 Shipping Info'