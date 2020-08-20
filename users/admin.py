from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from main_app.models import Cart
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db import IntegrityError

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CartInline(admin.TabularInline):
  model = Cart
  can_delete = True
  extra = 1 # Number of extra forms the formset will display in addition to the initial forms
  can_delete = True

  readonly_fields = (
    'get_item_count', 
    'get_subtotal',
    'get_total',
    'ordered_at',
    'closed_at'
  )

  show_change_link = True

class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = CustomUser

  # Fields displayed in the list page
  list_display = (
    'id',
    'email', 
    'first_name', 
    'last_name', 
    'company_name', 
    'business_phone', 
    'date_joined', 
    'is_active',
    'is_staff',
    'is_superuser', 
  )

  list_display_links = (
    'id', 
    'email',
  )

  # Field that can be editted directly within the list page
  list_editable = ('is_active',)

  # Filters in the right sidebar of the list page
  list_filter = (
    'date_joined', 
    'is_active', 
    'is_staff', 
    'is_superuser',
    'company_name',
  )

  # fieldsets control the layout of the change page
  fieldsets = (
    ('Login Credentials', {
      'fields': (
        ('first_name', 'last_name',),
        'email', 
        'password',
      )
    }),
    ('Business Details', {
      'fields': (
        'company_name', 
        'business_phone', 
        ('country_iso', 'province_iso'),
        ('city', 'address', 'postal_code',),
        'hst_number',
        'tax_percent',
        'discount_percent',
      )
    }),
    ('Permissions', {
      'description': 'Permission related fields',
      'fields': (
        'is_staff', 
        'is_active', 
        'is_superuser',
        # 'groups', 
        # 'user_permissions',
      )
    }),
  )

  # add_fieldsets control the layout of the add page
  add_fieldsets = (
    (None, {
      'fields': (
        ('first_name', 'last_name',),
        'email',
        ('password1', 'password2',),
      )
    }),
    ('Business Details', {
      'fields': (
        'company_name', 
        'business_phone', 
        ('country_iso', 'province_iso'),
        ('city', 'address', 'postal_code',),
        'hst_number',
        'tax_percent',
        'discount_percent',
      )
    }),
    ('Permissions', {
      'description': 'Permission related fields',
      'fields': (
        'is_staff', 
        'is_active', 
        'is_superuser',
        # 'groups',
        # 'user_permissions',
      )
    }),
  )
  search_fields = (
    'email',
    'first_name',
    'last_name',
    'company_name',
    'province_iso',
    'city',
  )
  ordering = ('date_joined',)

  inlines = (CartInline,)

  # Override changeform_view to handle IntegrityError when UniqueConstraint on user and status, where status = 1
  # This is because Django does not throw a ValidationError when using UnqieConstraint with condition(s)
  def changeform_view(self, req, *args, **kwargs):
    try:
      return super().changeform_view(req, *args, **kwargs)
    except IntegrityError as err:
      if 'unique_current_cart' in str(err):
        err = f"{req.user.full_name} already has a current cart (can\'t have more than one cart with 'Current' status)"
      self.message_user(req, str(err), level=messages.ERROR)
      return HttpResponseRedirect(req.path)

# ────────────────────────────────────────────────────────────────────────────────

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.site_header = 'ROADSTAR TIRE WHOLESALE'
admin.site.site_title = 'Roadstar Tire Wholesale'
admin.site.index_title = 'Site Admin'