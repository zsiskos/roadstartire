from django import forms
from users.models import CustomUser

class CustomUserEditForm(forms.ModelForm):
  COUNTRY_CHOICES = [
    ('CAN', 'Canada'),
    ('USA', 'United States')
  ]
  PROVINCE_CHOICES = [
    ('AB', 'Alberta'),
    ('BC', 'British Columbia'),
    ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'),
    ('NL', 'Newfoundland and Labrador'),
    ('NS','Nova Scotia'),
    ('NT', 'Northwest Territories'),
    ('NU', 'Nunavut'),
    ('ON', 'Ontario'), # Default
    ('PE','Prince Edward Island'),
    ('QC', 'Quebec'),
    ('SK', 'Saskatchewan'),
    ('YT', 'Yukon'),
  ]
  class Meta:
    model = CustomUser
    fields = ['company_name', 'hst_number', 'first_name', 'last_name', 'email', 'business_phone', 'address', 'city', 'postal_code', 'province_iso', 'country_iso']

# THIS USES DJANGO PURE FORMS AND IS LEFT IN AS AN EXAMPLE
# class CustomUserEditForm(forms.Form):
#   COUNTRY_CHOICES = [
#     ('CAN', 'Canada'),
#     ('USA', 'United States')
#   ]

#   PROVINCE_CHOICES = [
#     ('AB', 'Alberta'),
#     ('BC', 'British Columbia'),
#     ('MB', 'Manitoba'),
#     ('NB', 'New Brunswick'),
#     ('NL', 'Newfoundland and Labrador'),
#     ('NS','Nova Scotia'),
#     ('NT', 'Northwest Territories'),
#     ('NU', 'Nunavut'),
#     ('ON', 'Ontario'), # Default
#     ('PE','Prince Edward Island'),
#     ('QC', 'Quebec'),
#     ('SK', 'Saskatchewan'),
#     ('YT', 'Yukon'),
#   ]
#   company_name = forms.CharField(label='Company')
#   hst_number = forms.CharField(label='HST number')
#   first_name = forms.CharField()
#   last_name = forms.CharField()
#   email = forms.EmailField()
#   business_phone = forms.CharField(label='Phone')
#   address = forms.CharField()
#   city = forms.CharField()
#   province_iso = forms.ChoiceField(choices=PROVINCE_CHOICES, label='Province')
#   postal_code = forms.CharField()
#   country_iso = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Country')