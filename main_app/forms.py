from django import forms
from users.models import CustomUser
from django.core.exceptions import ValidationError

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

class CustomUserCreationForm(forms.Form):
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
  first_name = forms.CharField()
  last_name = forms.CharField()
  email = forms.EmailField()
  password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput) #widget sets field as a password field
  password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
  company_name = forms.CharField(label='Enter company name')
  hst_number = forms.CharField(label='Enter HST number')
  business_phone = forms.CharField(label='Phone')
  address = forms.CharField()
  city = forms.CharField()
  province_iso = forms.ChoiceField(choices=PROVINCE_CHOICES, label='Province')
  postal_code = forms.CharField()
  country_iso = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Country')

  # #cleans all of the inputs and returns then for saving in a later method
  # def clean_everything(self):
  #   first_name = self.cleaned_data['first_name'].title()
  #   last_name = self.cleaned_data['last_name'].title()
  #   company_name = self.cleaned_data['company_name'].title()
  #   hst_number = self.cleaned_data['hst_number'].upper()
  #   business_phone = self.cleaned_data['business_phone']
  #   address = self.cleaned_data['address'].title()
  #   city = self.cleaned_data['city'].title()
  #   postal_code = self.cleaned_data['postal_code'].upper()
  #   return first_name, last_name, company_name, hst_number, business_phone, address, city, postal_code

  #cleans email and checks if it exists
  def clean_email(self):
    email = self.cleaned_data['email'].lower()
    e = CustomUser.objects.filter(email=email)
    if e.count():
      raise ValidationError("An account with this email already exists")
    return email

  #cleans password and checks if they are the same
  def clean_password2(self):
    password1 = self.cleaned_data.get('password1')
    password2 = self.cleaned_data.get('password2')

    if password1 and password2 and password1 != password2:
      raise ValidationError("Passwords don't match")
    return password2

  #saves everything to the CustomUser model
  def save(self, commit=True):
    user = CustomUser.objects.create_user( #use create_user instead of create to trigger validation
      first_name=self.cleaned_data['first_name'].title(),
      last_name=self.cleaned_data['last_name'].title(),
      email=self.cleaned_data['email'].lower(),
      password=self.cleaned_data['password1'],
      company_name=self.cleaned_data['company_name'].title(),
      hst_number=self.cleaned_data['hst_number'].upper(),
      business_phone=self.cleaned_data['business_phone'],
      address=self.cleaned_data['address'].title(),
      city=self.cleaned_data['city'].title(),
      province_iso=self.cleaned_data['province_iso'],
      postal_code=self.cleaned_data['postal_code'].title(),
      country_iso=self.cleaned_data['country_iso']
    )
    return user


  #USER MODEL FOR REFERENCE
  # email = models.EmailField(unique=True)
  # first_name = models.CharField(max_length=30)
  # last_name = models.CharField(max_length=30)
  # is_active = models.BooleanField(default=True, help_text=is_active_help_text)
  # is_staff = models.BooleanField(default=False, help_text=is_staff_help_text)
  # date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Date Joined (UTC)')
  # company_name = models.CharField(max_length=50, blank=True, verbose_name='Company')
  # business_phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
  # country_iso = models.CharField(max_length=3, choices=COUNTRY_CHOICES, default=COUNTRY_CHOICES[0][0], verbose_name='Country')
  # province_iso = models.CharField(max_length=2, choices=PROVINCE_CHOICES, default=PROVINCE_CHOICES[8][0], verbose_name='Province')
  # city = models.CharField(max_length=30, blank=True)
  # address = models.CharField(max_length=30, blank=True)
  # postal_code = models.CharField(max_length=30, blank=True)
  # hst_number = models.CharField(max_length=30, blank=True, verbose_name='HST Number')
  # discount_ratio = models.DecimalField(
  #   max_digits=4, 
  #   decimal_places=2, 
  #   default=0, 
  #   verbose_name='Discount', 
  #   validators=[MinValueValidator(0), MaxValueValidator(1),], 
  #   help_text=discount_ratio_help_text
  # )