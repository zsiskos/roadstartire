from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms


from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm):
    model = CustomUser
    fields = (
      'first_name', 
      'last_name', 
      'email', 
      'company_name', 
      'hst_number', 
      'business_phone', 
      'address', 
      'city', 
      'postal_code', 
      'province_iso', 
      'country_iso',)

class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = CustomUser
    fields = ['company_name', 'hst_number', 'first_name', 'last_name', 'email', 'business_phone', 'address', 'city', 'postal_code', 'province_iso', 'country_iso']

