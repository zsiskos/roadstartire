from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms


from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
  def __init__(self, *args, **kwargs):
      super(CustomUserCreationForm, self).__init__(*args, **kwargs)
      for field in self.fields:
          self.fields[field].widget.attrs['class'] = 'form-control'

  class Meta(UserCreationForm):
    model = CustomUser
    fields = (
      'first_name', 
      'last_name', 
      'email', 
      'company_name', 
      'gst_number', 
      'business_phone', 
      'address', 
      'address_2', 
      'city', 
      'postal_code', 
      'province_iso', 
      'country_iso',
      'timezone',)

class CustomUserChangeForm(UserChangeForm):
  password = None

  def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
  class Meta:
    model = CustomUser
    fields = (
      'company_name', 
      'gst_number',
      'first_name',
      'last_name',
      'email',
      'business_phone',
      'address',
      'address_2', 
      'city',
      'postal_code',
      'province_iso',
      'country_iso',
      'timezone',)