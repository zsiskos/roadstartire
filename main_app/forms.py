from django import forms
from users.models import CustomUser
from main_app.models import CartDetail
from django.core.exceptions import ValidationError

class CustomUserEditForm(forms.ModelForm):
  class Meta:
    model = CustomUser
    fields = ['company_name', 'hst_number', 'first_name', 'last_name', 'email', 'business_phone', 'address', 'city', 'postal_code', 'province_iso', 'country_iso']

class CartDetailCreationForm(forms.ModelForm):
  class Meta:
    model = CartDetail
    fields = [
      'quantity',
    ]

# THIS USES DJANGO PURE FORMS AND IS LEFT IN AS AN EXAMPLE
# class CustomUserCreationForm2(forms.Form):
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
#   first_name = forms.CharField()
#   last_name = forms.CharField()
#   email = forms.EmailField()
#   password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput) #widget sets field as a password field
#   password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
#   company_name = forms.CharField(label='Enter company name')
#   hst_number = forms.CharField(label='Enter HST number')
#   business_phone = forms.CharField(label='Phone')
#   address = forms.CharField()
#   city = forms.CharField()
#   province_iso = forms.ChoiceField(choices=PROVINCE_CHOICES, label='Province')
#   postal_code = forms.CharField()
#   country_iso = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Country')

#   #cleans email and checks if it exists
#   def clean_email(self):
#     email = self.cleaned_data['email'].lower()
#     e = CustomUser.objects.filter(email=email)
#     if e:
#       raise ValidationError("An account with this email already exists")
#     return email

#   #cleans password and checks if they are the same
#   def clean_password2(self):
#     password1 = self.cleaned_data.get('password1')
#     password2 = self.cleaned_data.get('password2')

#     if password1 and password2 and password1 != password2:
#       raise ValidationError("Passwords don't match")
#     return password2

#   #cleaned and transforms data, then saves everything to the CustomUser model
#   def save(self, commit=True):
#     user = CustomUser.objects.create_user( #use create_user instead of create to trigger validation
#       first_name=self.cleaned_data['first_name'].title(),
#       last_name=self.cleaned_data['last_name'].title(),
#       email=self.cleaned_data['email'].lower(),
#       password=self.cleaned_data['password1'],
#       company_name=self.cleaned_data['company_name'].title(),
#       hst_number=self.cleaned_data['hst_number'].upper(),
#       business_phone=self.cleaned_data['business_phone'],
#       address=self.cleaned_data['address'].title(),
#       city=self.cleaned_data['city'].title(),
#       province_iso=self.cleaned_data['province_iso'],
#       postal_code=self.cleaned_data['postal_code'].title(),
#       country_iso=self.cleaned_data['country_iso']
#     )
#     return user
