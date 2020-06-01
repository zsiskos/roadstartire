from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = CustomUser

  # Fields displayed in the list page
  list_display = (
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
        'is_active',
        'is_staff',
        'is_superuser',
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

# ────────────────────────────────────────────────────────────────────────────────

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.site_header = 'Road Star Tire Admin'
admin.site.site_tite = 'Road Star Tire Admin'