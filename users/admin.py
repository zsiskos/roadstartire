from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from main_app.models import Cart

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
  )

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
        'discount_ratio',
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
        'discount_ratio',
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
    'province',
    'city',
  )
  ordering = ('date_joined',)

  inlines = (CartInline,)

# ────────────────────────────────────────────────────────────────────────────────

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.site_header = 'Road Star Tire'
admin.site.site_title = 'Road Star Tire'
admin.site.index_title = 'Site Admin'