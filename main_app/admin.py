from django.contrib import admin
from .models import Cart, Tire, CartDetail, OrderShipping, Tread, Image, Product, Stock
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils import timezone
from django.utils.html import format_html
from django.forms.models import BaseInlineFormSet
import datetime
from copy import deepcopy
from django.db.models import Q
import os
import environ

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
    'product',
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
        'product',
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
      return ('cart', 'product', 'price_each', 'created_at', 'updated_at',)
    else: # Add view
      return ('price_each', 'created_at', 'updated_at',)

  autocomplete_fields = ['product',]

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailInline(admin.TabularInline):
  model = CartDetail
  can_delete = True
  extra = 1
  show_change_link = True

  readonly_fields = (
    'price',
    'get_subtotal',
    'created_at',
    'updated_at',
  )

  fields = (
    'product',
    'quantity',
    'price',
    'get_subtotal',
    'created_at',
    'updated_at',
  )

  autocomplete_fields = ['product']

# ────────────────────────────────────────────────────────────────────────────────

class ImageInline(admin.StackedInline):
  model = Image
  # can_delete = False
  extra = 1
  # show_change_link = True

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

# ────────────────────────────────────────────────────────────────────────────────

class CartAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'get_order_number',
    'user',
    'get_full_name',
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

  def get_readonly_fields(self, request, obj=None):
    if obj: # Change view
      return (
        'user',
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
    else: # Add view
      return (
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

  def get_total(self, obj):
    return format_html("<b style='color: red'>{}</b>", obj.get_total())
  get_total.short_description = format_html("<b style='color: red';>{}</b>", 'Total ($)')


# ────────────────────────────────────────────────────────────────────────────────

class TireAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'product_num',
    'product',
    'price',
    'sale_price',
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'tire_type',
    'pattern',
    'tread',
    'load_speed',
    # 'is_effective', # Hide until fully implemented
  )

  list_display_links = (
    'id',
    'product_num',
    'product',
  )

  list_filter = (
    'brand',
    'year',
    'tire_type',
    'tread',
  )

  search_fields = (
    'product__id',
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'load_speed',
    'pattern',
    'tread__name',
  )

  # Dynamic fieldsets
  def get_fieldsets(self, request, obj=None):
    if obj: # Change view
      fieldsets = (
        (None, {
          'fields': (
            'product_num',
            'product',
            'get_image_display',
            'price',
            'sale_price',
            'brand',
            'year',
            'width',
            'aspect_ratio',
            'rim_size',
            'tire_type',
            ('pattern', 'tread',),
            'load_speed',
            # 'updated_to', # Hide in production
            # 'inherits_from', # Hide in production
            # 'date_effective', # Hide until fully implemented
            # 'get_date_effective_delta', # Hide until fully implemented
            # 'is_effective', # Hide until fully implemented
          )
        }),
      )
    else: # Add view
      fieldsets = (
        (None, {
          'fields': (
            'product',
            'price',
            'sale_price',
            'brand',
            'year',
            'width',
            'aspect_ratio',
            'rim_size',
            'tire_type',
            ('pattern', 'tread',),
            'load_speed',
          )
        }),
      )
    return fieldsets

  # Dynamic readonly
  def get_readonly_fields(self, request, obj=None):
    if obj: # Change view
      if obj.updated_to:
        return (
        'product_num',
        'product',
        'name',
        'updated_to',
        'inherits_from',
        'sold_online_quantity',
        'sold_offline_quantity',
        'sold_quantity',
        'lost_quantity',
        'other_quantity',
        'decrease_quantity',
        'current_quantity',
        'total_quantity',
        'get_image_display',
        'get_date_effective_delta',
        'is_effective',
        'price',
        'sale_price',
        'brand',
        'year',
        'width',
        'aspect_ratio',
        'rim_size',
        'tire_type',
        'pattern',
        'tread',
        'load_speed',
      )
      return (
        'product_num',
        'product',
        'name',
        'updated_to',
        'inherits_from',
        'sold_online_quantity',
        'sold_offline_quantity',
        'sold_quantity',
        'lost_quantity',
        'other_quantity',
        'decrease_quantity',
        'current_quantity',
        'total_quantity',
        'get_image_display',
        'get_date_effective_delta',
        'is_effective',
      )
      return (
        'product_num',
        'product',
        'name',
        'updated_to',
        'inherits_from',
        'sold_online_quantity',
        'sold_offline_quantity',
        'sold_quantity',
        'lost_quantity',
        'other_quantity',
        'decrease_quantity',
        'current_quantity',
        'total_quantity',
        'get_image_display',
        'get_date_effective_delta',
        'is_effective',
      )
    else: # Add view
      return ()

  autocomplete_fields = (
    'product',
    'tread',
  )

  def save_model(self, request, obj, form, change):
    if change:
      old_obj = deepcopy(obj)
      obj.id = None # Set to None so that new row is inserted
      obj.inherits_from = old_obj
      obj.date_effective = timezone.now() # Default to current time for now until can find a way to filter the tire_list queryset proprerly
      obj.save()
    super().save_model(request, obj, form, change)
    
  save_as = False

  def has_add_permission(self, request, obj=None):
    return False # Tires should be added from the Product Add view

  # Product objects should not exist without tires
  def has_delete_permission(self, request, obj=None):
    print(os.environ['DEBUG_VALUE'])
    if os.environ['DEBUG_VALUE'] == 'True':
      return True
    return False

  def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    extra_context = extra_context or {}
    extra_context['show_save_and_continue'] = False
    extra_context['show_save'] = True
    return super(TireAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

  # Lists most recent version (regardless of its effective date)
  # def get_queryset(self, request):
  #   qs = super(TireAdmin, self).get_queryset(request)
  #   return qs.filter(updated_to=None)

  # Lists most recent viable version (only allows for 2 queued tire versions and then breaks afterwards...)
  # TODO: Allow filter to check beyond two versions deep from the most recently added tire
  # def get_queryset(self, request):
  #   qs = super(TireAdmin, self).get_queryset(request)
  #   return qs.filter (
  #     (Q(updated_to=None) & Q(date_effective__lte=timezone.now())) | 
  #     (Q(updated_to__updated_to=None) & Q(updated_to__date_effective__gte=timezone.now()))
  #   )

  # Prepopulate the date_effective field with the current time
  # TODO: Presents the current time but doesn't allow user to enter a different time in the form
  # def get_form(self, request, obj=None, **kwargs):
  #   form = super(TireAdmin, self).get_form(request, obj, **kwargs)
  #   if obj:
  #     obj.date_effective = timezone.now()
  #   return form

  def get_image_display(self, obj):
    if obj.tread:
      return obj.tread.image_set.first().get_image_display()
    return format_html("<img style='border: 1px solid lightgray; border-radius: 8px' width={width} height={height}/>".format(
        width = 100, # hardcoded thumbnail dimensions
        height = 100,
        )
      )
  get_image_display.short_description = 'Thumbnail'

# ────────────────────────────────────────────────────────────────────────────────

class OrderShippingAdmin(admin.ModelAdmin):
  list_display = (
    'order_number',
    # 'cart',
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
    'province_iso',
    'city',
  )

  search_fields = (
    'pk',
    'cart__pk',
    'first_name',
    'last_name',
    'city',
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

# ────────────────────────────────────────────────────────────────────────────────

class TireBaseInlineFormset(BaseInlineFormSet): 
  def get_queryset(self) :
    qs = super(TireBaseInlineFormset, self).get_queryset()
    return qs.order_by('-id')[:1] # Inline should show the most recently added tire
    # return qs.filter(updated_to=None) # Inline should show the most recently added tire

  def save_existing(self, form, instance, commit=True):
    old_instance = deepcopy(instance)
    instance.id = None # Set id to None to save as new
    instance.inherits_from = old_instance
    return form.save(commit=commit)

class TireInline(admin.StackedInline):
  model = Tire
  can_delete = False
  extra = 1
  max_num = 1
  show_change_link = True
  formset = TireBaseInlineFormset
  
  fieldsets = (
    (None, {
      'fields': (
        'price',
        'sale_price',
        'brand',
        'year',
        'width',
        'aspect_ratio',
        'rim_size',
        'tire_type',
        ('pattern', 'tread',),
        'load_speed',
        # 'date_effective', # Hide until fully implemented
        # 'get_date_effective_delta', # Hide until fully implemented
      )
    }),
  )

  readonly_fields = (
    'name',
    'get_date_effective_delta',
  )

  autocomplete_fields = (
    'tread',
  )

# ────────────────────────────────────────────────────────────────────────────────

class StockInline(admin.TabularInline):
  model = Stock
  can_delete = True
  extra = 1
  # show_change_link = True

  readonly_fields = (   
    'created_at',
    'updated_at',)

# ────────────────────────────────────────────────────────────────────────────────

class ProductAdmin(admin.ModelAdmin):
  list_display = (
    'id',
    'name',
    'price',
    'sale_price',
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'tire_type',
    'pattern',
    'tread',
    'load_speed',
    # 'sold_quantity',
    # 'decrease_quantity',
    # 'current_quantity',
  )

  list_display_links = (
    'id',
    'name',
  )

  list_filter = (
    'is_archived',
  )

  search_fields = (
    'id',
    'tire__brand',
    'tire__year',
    'tire__width',
    'tire__aspect_ratio',
    'tire__rim_size',
    'tire__tire_type',
    'tire__pattern',
    'tire__tread__name',
    'tire__load_speed',
  )

  readonly_fields = (
    'id',
    'name',
    'sold_online_quantity',
    'sold_offline_quantity',
    'sold_quantity',
    'shrink_quantity',
    # 'lost_quantity',
    # 'other_quantity',
    # 'decrease_quantity',
    'current_quantity',
    'total_quantity',
    'get_image_display',
  )

  # Dynamic fieldsets
  def get_fieldsets(self, request, obj=None):
    if obj: # Change view
      fieldsets = (
        (None, {
          'fields': (
            'id',
            'name',
            'get_image_display',
            'sold_online_quantity', 
            'sold_offline_quantity',
            'shrink_quantity',
            # ('lost_quantity', 'other_quantity',),
            'current_quantity',
            'total_quantity',
            # 'is_archived', # Hide until fully implemented
          )
        }),
      )
    else: # Add view
      fieldsets = (
        (None, {
          'fields': (
            # 'is_archived', # Hide until fully implemented
          )
        }),
      )
    return fieldsets

  inlines = (StockInline, TireInline)

  def get_queryset(self, request):
    qs = super(ProductAdmin, self).get_queryset(request)
    return qs.filter( # Need this filter so to remove duplicate rows when sorting on calculated fields)
      (Q(tire__updated_to=None) & Q(tire__date_effective__lte=timezone.now())) | 
      (Q(tire__updated_to__updated_to=None) & Q(tire__updated_to__date_effective__gte=timezone.now()))
      )

  def get_image_display(self, obj):
    if obj.get_current().tread:
      return obj.get_current().tread.image_set.first().get_image_display()
    return format_html("<img style='border: 1px solid lightgray; border-radius: 8px' width={width} height={height}/>".format(
        width = 100, # hardcoded thumbnail dimensions
        height = 100,
        )
      )
  get_image_display.short_description = 'Thumbnail'

  # Product should never be deleted -> Use archive feature instead
  def has_delete_permission(self, request, obj=None):
    if os.environ['DEBUG_VALUE'] == 'True':
      return True
    return False

# ────────────────────────────────────────────────────────────────────────────────

class StockAdmin(admin.ModelAdmin):
  list_display = (
    'product',
    'quantity_change_type',
    'quantity_change_value',
    'created_at',
    'updated_at',
  )

  list_filter = (
    'quantity_change_type',
    'created_at',
    'updated_at',
  )

  list_editable = (
    'quantity_change_type',
  )
  
  autocomplete_fields = (
    'product',
  )

  search_fields = (
    'product__id',
  )

  # Dynamic fieldsets
  def get_fieldsets(self, request, obj=None):
    if obj: # Change view
      fieldsets = (
        (None, {
          'fields': (
            'product',
            'quantity_change_type',
            'quantity_change_value',
            'created_at',
            'updated_at',
          )
        }),
      )
    else: # Add view
      fieldsets = (
        (None, {
          'fields': (
            'product',
            'quantity_change_type',
            'quantity_change_value',
          )
        }),
      )
    return fieldsets

  # Dynamic readonly
  def get_readonly_fields(self, request, obj=None):
    if obj: # Change view
      return (
        'product',
        'created_at',
        'updated_at',
      )
    else: # Add view
      return (
        'created_at',
        'updated_at',
      )

# ────────────────────────────────────────────────────────────────────────────────

# Register your models here
admin.site.register(Cart, CartAdmin)
admin.site.register(OrderShipping, OrderShippingAdmin)
admin.site.register(Tread, TreadAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Stock, StockAdmin)

# Hide these models in production
if os.environ['DEBUG_VALUE'] == 'True':
  admin.site.register(CartDetail, CartDetailAdmin)
if os.environ['DEBUG_VALUE'] == 'True':
  admin.site.register(Tire, TireAdmin)
if os.environ['DEBUG_VALUE'] == 'True':
  admin.site.register(Image, ImageAdmin)