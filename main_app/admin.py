from django.contrib import admin
from .models import Cart, Tire, CartDetail
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils import timezone

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
    if obj:
      return ('cart', 'tire', 'price_each', 'created_at', 'updated_at',) # Existing object
    else:
      return ('price_each', 'created_at', 'updated_at',) # Creating an object

  autocomplete_fields = ['tire']

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailInline(admin.TabularInline):
  model = CartDetail
  can_delete = True
  extra = 1 # Number of extra forms the formset will display in addition to the initial forms

  readonly_fields = (
    'price_each',
    'get_subtotal',
    'created_at',
    'updated_at'
  )

  autocomplete_fields = ['tire']

# ────────────────────────────────────────────────────────────────────────────────

class CartAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'user',
    'get_owner',
    'created_at',
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
    'created_at',
    'updated_at',
    'ordered_at',
    'status',
  )

  search_fields = (
    'user__first_name',
    'user__last_name',
    'user__email',
  )

  fieldsets = (
    (None, {
      'fields': (
        'user',
        'status',
        'get_item_count', 
        'discount_ratio_applied',
        'get_subtotal',
        'tax',
        'get_total',
        'created_at',
        'updated_at',
        'ordered_at',
        'closed_at',
      )
    }),
  )

  readonly_fields = (
    'get_item_count', 
    'get_subtotal',
    'get_total',
    'created_at',
    'updated_at',
    'ordered_at',
    'closed_at',
  )

  inlines = (CartDetailInline,)

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
      "%d cart was successfully changed and marked as 'Fulfilled'.",
      "%d carts were successfully changed and marked as 'Fulfilled'.",
      updated,
    ) % updated, messages.SUCCESS)
  mark_as_fulfilled.short_description = "Mark selected carts as 'Fulfilled'"

  def mark_as_cancelled(self, req, queryset):
    updated = 0
    for cart in queryset:
      if cart.status != Cart.Status.CANCELLED:
        updated += 1
      cart.status=Cart.Status.CANCELLED
      cart.save()
    self.message_user(req, ngettext(
      "%d cart was successfully changed and marked as 'Cancelled'.",
      "%d carts were successfully changed and marked as 'Cancelled'.",
      updated,
    ) % updated, messages.SUCCESS)
  mark_as_cancelled.short_description = "Mark selected carts as 'Cancelled'"
  
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