from django.contrib import admin
from .models import Cart, Tire, CartDetail, OrderShipping, Tread, Image
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils import timezone
from django.utils.html import format_html

# ────────────────────────────────────────────────────────────────────────────────
# list_display - Controls which fields are displayed on the change list page
# list_display_links - Controls if and which fields in list_display should be linked to the “change” page for an object
# list_editable - List of field names on the model which will allow editing on the change list page
# list_filter - Filters in the right sidebar of the change list page

# https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
# https://docs.djangoproject.com/en/3.0/intro/tutorial07/
# ────────────────────────────────────────────────────────────────────────────────

admin.site.empty_value_display = '–'

# ────────────────────────────────────────────────────────────────────────────────

class OrderShippingInline(admin.StackedInline):
  model = OrderShipping
  can_delete = False
  extra = 0 # Set to 0 to hide the form when there is no OrderShipping
  show_change_link = True

  readonly_fields = (
    'first_name',
    'last_name',
    'company_name',
    'business_phone',
    'country_iso',
    'province_iso',
    'city',
    'address',
    'address_2',
    'postal_code',
    'gst_number',
  )

  fieldsets = (
    (None, {
      'fields': (
        'first_name', 
        'last_name',
        'company_name',
        'business_phone',
        'country_iso', 'province_iso',
        'city', 'address','address_2', 'postal_code',
        'gst_number',
      )
    }),
  )

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'cart',
    'tire',
    'price_each',
    'quantity',
    'get_subtotal',
    'created_at',
    'updated_at',
  )

  list_display_links = (
    'id',
    'cart',
  )
  
  list_editable = ('quantity',)

  fieldsets = (
    (None, {
      'fields': (
        'cart',
        'tire',
        'price_each', # Should not be able to edit price directly
        'quantity',
        'created_at',
        'updated_at',
      )
    }),
  )

  # Dynamic readonly
  def get_readonly_fields(self, request, obj=None):
    if obj: # Change view
      return ('cart', 'tire', 'price_each', 'created_at', 'updated_at',)
    else: # Add view
      return ('price_each', 'created_at', 'updated_at',)

  autocomplete_fields = ['tire']

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailInline(admin.TabularInline):
  model = CartDetail
  can_delete = True
  extra = 1
  show_change_link = True

  readonly_fields = (
    'price_each',
    'get_subtotal',
    'created_at',
    'updated_at'
  )

  autocomplete_fields = ['tire']

# ────────────────────────────────────────────────────────────────────────────────

class ImageInline(admin.StackedInline):
  model = Image
  # can_delete = False
  extra = 0 # Set to 0 to hide the form when there is no OrderShipping
  # show_change_link = True

  readonly_fields = (
    'get_image_display',
  )

  def get_image_display(self, obj):
    return format_html('<img src="{url}" width={width} height={height} />'.format(
      url = obj.url,
      width = 100, # hardcoded thumbnail dimensions
      height = 100,
      )
    )
  get_image_display.short_description = 'Thumbnail'

# ────────────────────────────────────────────────────────────────────────────────

class CartAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'get_order_number',
    'user',
    'get_owner',
    'created_at',
    'status',
    'get_item_count',
    'get_subtotal',
    'get_discount_amount',
    'get_tax_amount',
    'get_total',
  )

  list_display_links = (
    'id',
    'get_order_number',
    'user',
  )

  list_editable = ('status',)

  list_filter = (
    'created_at',
    'updated_at',
    'ordered_at',
    'status',
  )

  search_fields = (
    'pk',
    'ordershipping__pk',
    'user__first_name',
    'user__last_name',
    'user__email',
  )

  # Dynamic fieldsets
  def get_fieldsets(self, request, obj=None):
    if obj: # Change view
      fieldsets = (
        (None, {
          'fields': (
            'user',
            'status',
            'get_item_count', 
            'get_subtotal',
            (
              'get_discount_amount',
              'discount_percent_applied',
            ),
            (
              'get_tax_amount',
              'tax_percent_applied',
            ),
            'get_total',
            'created_at',
            'updated_at',
            'ordered_at',
            'closed_at',
          )
        }),
      )
    else: # Add view
      fieldsets = (
        (None, {
          'fields': (
            'user',
            'status',
          )
        }),
      )
    return fieldsets

  readonly_fields = (
    'get_order_number',
    'get_item_count', 
    'get_subtotal',
    'get_discount_amount',
    'get_tax_amount',
    'get_total',
    'created_at',
    'updated_at',
    'ordered_at',
    'closed_at',
  )

  # Dynamic inlines
  def get_inlines(self, request, obj):
    if obj is None: # Add view
      return (CartDetailInline,)
    return (OrderShippingInline, CartDetailInline,) # Change view

  actions = [
    'mark_as_cancelled',
    'mark_as_fulfilled',
  ] 

  def mark_as_fulfilled(self, req, queryset):
    updated = 0
    for cart in queryset:
      if cart.status != Cart.Status.FULFILLED:
        updated += 1
      cart.status=Cart.Status.FULFILLED
      cart.save()
    self.message_user(req, ngettext(
      "%d cart was successfully changed and marked as '✅ Fulfilled'.",
      "%d carts were successfully changed and marked as '✅ Fulfilled'.",
      updated,
    ) % updated, messages.SUCCESS)
  mark_as_fulfilled.short_description = "Mark selected carts as '✅ Fulfilled'"

  def mark_as_cancelled(self, req, queryset):
    updated = 0
    for cart in queryset:
      if cart.status != Cart.Status.CANCELLED:
        updated += 1
      cart.status=Cart.Status.CANCELLED
      cart.save()
    self.message_user(req, ngettext(
      "%d cart was successfully changed and marked as '❌ Cancelled'.",
      "%d carts were successfully changed and marked as '❌ Cancelled'.",
      updated,
    ) % updated, messages.SUCCESS)
  mark_as_cancelled.short_description = "Mark selected carts as '❌ Cancelled'"
  
  # Override changeform_view and changelist_view to handle IntegrityError when UniqueConstraint on user and status, where status = 1
  # This is because Django does not throw a ValidationError when using UnqieConstraint with condition(s)
  def changeform_view(self, req, *args, **kwargs):
    try:
      return super().changeform_view(req, *args, **kwargs)
    except IntegrityError as err:
      if 'unique_current_cart' in str(err):
        err = f"{req.user.full_name} already has a current cart (can\'t have more than one cart with 'Current' status)"
      self.message_user(req, str(err), level=messages.ERROR)
      return HttpResponseRedirect(req.path)

  def changelist_view(self, req, *args, **kwargs):
    try:
      return super().changelist_view(req, *args, **kwargs)
    except IntegrityError as err:
      if 'unique_current_cart' in str(err):
        err = "Can\'t have more than one cart with 'Current' status"
      self.message_user(req, str(err), level=messages.ERROR)
      return HttpResponseRedirect(req.path)

  date_hierarchy = 'created_at'

  autocomplete_fields = ['user']

  # Dynamic choice fields
  def formfield_for_choice_field(self, db_field, request, **kwargs):
    if db_field.name == "status":
      kwargs['choices'] = (
        (Cart.Status.CURRENT, '1. 🛒 Current'),
        (Cart.Status.IN_PROGRESS, '2. ⏳ In Progress'),
        (Cart.Status.FULFILLED, '3. ✅ Fulfilled'),
        (Cart.Status.CANCELLED, '❌ Cancelled'),
        (Cart.Status.ABANDONED, '🚧 Abandoned'),  
      )
    # if request.user.is_superuser:
    #   kwargs['choices'] += (('ready', 'Ready for deployment'),)
    return super().formfield_for_choice_field(db_field, request, **kwargs)

# ────────────────────────────────────────────────────────────────────────────────

class TireAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'name',
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'tire_type',
    'pattern',
    'load_speed',
    'tread',
    'price',
    'sale_price',
    'current_quantity',
    'sold',
    'get_total_quantity',
  )

  list_display_links = (
    'id',
    'name',
  )

  list_filter = (
    'brand',
    'year',
    'tire_type',
    'tread',
  )

  search_fields = (
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'load_speed',
  )

  # Dynamic fieldsets
  def get_fieldsets(self, request, obj=None):
    if obj: # Change view
      fieldsets = (
        (None, {
          'fields': (
            'name',
            'brand',
            'year',
            (
              'width',
              'aspect_ratio',
              'rim_size',
              'tire_type',
              'pattern',
              'load_speed',
              'tread',
            ),
            'price',
            'sale_price',
          )
        }),
        ('Inventory', {
          'fields': (
            'current_quantity',
            'sold',
            'get_total_quantity',
          )
        }),
      )
    else: # Add view
      fieldsets = (
        (None, {
          'fields': (
            # 'name',
            'brand',
            'year',
            (
              'width',
              'aspect_ratio',
              'rim_size',
              'tire_type',
              'pattern',
              'load_speed',
              'tread',
            ),
            'price',
            'sale_price',
          )
        }),
        ('Inventory', {
          'fields': (
            'current_quantity',
            'sold',
            'get_total_quantity',
          )
        }),
      )
    return fieldsets

  readonly_fields = ('name', 'get_total_quantity',)

  autocomplete_fields = ['tread']

# ────────────────────────────────────────────────────────────────────────────────

class OrderShippingAdmin(admin.ModelAdmin):
  list_display = (
    '__str__',
    'cart',
    'first_name',
    'last_name',
    'company_name',
    'business_phone',
    'country_iso',
    'province_iso',
    'city',
    'address',
    'address_2',
    'postal_code',
    'gst_number',
  )

  list_filter = (
  
  )

  search_fields = (
    'pk',
    'cart__pk',
    'first_name',
    'last_name',
  )

  fieldsets = (
    (None, {
      'fields': (
        'cart',
        'first_name',
        'last_name',
        'company_name',
        'business_phone',
        'country_iso',
        'province_iso',
        'city',
        'address',
        'address_2',
        'postal_code',
        'gst_number',
      )
    }),
  )

  # Dynamic readonly
  def get_readonly_fields(self, request, obj=None):
    if obj:
      return ('cart',) # Existing object
    else:
      return ('',) # Creating an object

# ────────────────────────────────────────────────────────────────────────────────

class TreadAdmin(admin.ModelAdmin):
  list_display = (
    'name',
    'get_image_count',
  )

  search_fields = (
    'name',
  )

  readonly_fields = (
    'get_image_count',
  )

  inlines = (ImageInline,)

# ────────────────────────────────────────────────────────────────────────────────

class ImageAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'get_image_display',
    'url',
    'tread',
  )

  list_display_links = (
    'id',
    'get_image_display',
    'url',
  )

  list_filter = (
    'tread',
  )

  search_fields = (
    'tread',
  )

  # Dynamic fieldsets
  def get_fieldsets(self, request, obj=None):
    if obj: # Change view
      fieldsets = (
        (None, {
          'fields': (
            'get_image_display',
            'url',
          )
        }),
      )
    else: # Add view
      fieldsets = (
        (None, {
          'fields': (
            'url',
          )
        }),
      )
    return fieldsets

  readonly_fields = (
    'get_image_display',
  )

  autocomplete_fields = ['tread']

  def get_image_display(self, obj):
    return format_html('<img src="{url}" width={width} height={height} />'.format(
      url = obj.url,
      width = 100, # hardcoded thumbnail dimensions
      height = 100,
      )
    )
  get_image_display.short_description = 'Thumbnail'

# ────────────────────────────────────────────────────────────────────────────────

# Register your models here
admin.site.register(CartDetail, CartDetailAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Tire, TireAdmin)
admin.site.register(OrderShipping, OrderShippingAdmin)
admin.site.register(Tread, TreadAdmin)
admin.site.register(Image, ImageAdmin)
