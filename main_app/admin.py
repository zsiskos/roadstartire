from django.contrib import admin
from .models import Cart, Tire, CartDetail
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db import IntegrityError

# ────────────────────────────────────────────────────────────────────────────────
# list_display - Controls which fields are displayed on the change list page
# list_display_links - Controls if and which fields in list_display should be linked to the “change” page for an object
# list_editable - List of field names on the model which will allow editing on the change list page
# list_filter - Filters in the right sidebar of the change list page

# https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
# https://docs.djangoproject.com/en/3.0/intro/tutorial07/
# ────────────────────────────────────────────────────────────────────────────────

admin.site.empty_value_display = '–'

class CartDetailAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'cart',
    'tire',
    'price_each',
    'quantity',
    'get_subtotal',
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
      )
    }),
  )

  # Dynamic readonly
  def get_readonly_fields(self, request, obj=None):
    if obj:
      return ('cart', 'tire', 'price_each') # Existing object
    else:
      return ('price_each',) # Creating an object

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailInline(admin.TabularInline):
  model = CartDetail
  can_delete = True
  extra = 1 # Number of extra forms the formset will display in addition to the initial forms

  readonly_fields = (
    'price_each',
    'get_subtotal',
  )

# ────────────────────────────────────────────────────────────────────────────────

class CartAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'user',
    'get_owner',
    'date_ordered',
    'status',
    'get_item_count',
    'discount_ratio_applied',
    'get_subtotal',
    'get_total',
  )

  list_display_links = (
    'id',
    'user',
  )

  list_editable = ('status',)

  list_filter = (
    'date_ordered',
    'status',
  )

  search_fields = (
    'id',
    'user',
  )

  fieldsets = (
    (None, {
      'fields': (
        'user',
        'status',
        'get_item_count', 
        'discount_ratio_applied',
        'get_subtotal',
        'get_total',
      )
    }),
  )

  readonly_fields = (
    'get_item_count', 
    'get_subtotal',
     'get_total',
  )

  inlines = (CartDetailInline,)

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
        err = f"{req.user.full_name} already has a current cart (can\'t have more than one cart with 'Current' status)"
      self.message_user(req, str(err), level=messages.ERROR)
      return HttpResponseRedirect(req.path)

# ────────────────────────────────────────────────────────────────────────────────

class TireAdmin(admin.ModelAdmin):
  list_display = (
    'name',
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'season',
    'pattern',
    'load',
    'price',
    'sale_price',
    'current_quantity',
    'sold',
    'get_total_quantity',
  )

  list_filter = (
    'brand',
    'year',
    'season',
  )

  search_fields = (
    'name',
    'brand',
    'year',
  )

  fieldsets = (
    (None, {
      'fields': (
        'name',
        'brand',
        'year',
        'image',
        (
        'width',
        'aspect_ratio',
        'rim_size',
        'season',
        'pattern',
        'load',
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

  readonly_fields = ('get_total_quantity',)

# ────────────────────────────────────────────────────────────────────────────────

# Register your models here
admin.site.register(CartDetail, CartDetailAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Tire, TireAdmin)