from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm):
    model = CustomUser
    fields = ('email', 'company_name', 'hst_number', 'first_name', 'last_name', 'business_phone', 'address', 'city', 'postal_code', 'province_iso', 'country_iso')


class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = CustomUser
    fields = ('email',)

