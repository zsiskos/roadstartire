from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
  address = forms.CharField(widget= forms.TextInput(attrs={'placeholder':'Street address, P.O. box, c/o'}))
  address_2 = forms.CharField(label = _('Apt, suite, unit, etc. (optional)'), required = False)
  password2 = forms.CharField(label = _('Confirm password'), widget= forms.TextInput(attrs={'type': 'password'}))

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
      'province_iso',
      'postal_code',
      # 'country_iso',
      'timezone',
    )

class CustomUserChangeForm(UserChangeForm):
  password = None

  address = forms.CharField(widget= forms.TextInput(attrs={'placeholder':'Street address, P.O. box, c/o'}))
  
  address_2 = forms.CharField(label = _('Apt, suite, unit, etc. (optional) '), required = False)

  def __init__(self, *args, **kwargs):
    super(CustomUserChangeForm, self).__init__(*args, **kwargs)
    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'
      self.label_suffix = ""  # Removes : as label suffix
            
  class Meta(UserChangeForm):
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
      'province_iso',
      'postal_code',
      # 'country_iso',
      'timezone',)