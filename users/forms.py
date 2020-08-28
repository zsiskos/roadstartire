from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms import CharField


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
  password = None

  def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

  class Meta:
    model = CustomUser
    fields = ['company_name', 'hst_number', 'first_name', 'last_name', 'email', 'business_phone', 'address', 'city', 'postal_code', 'province_iso', 'country_iso']