from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.mail import send_mail, mail_admins
from django.shortcuts import render, redirect
from django.views.generic import ListView
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser
from django.contrib.auth import login
from django.db.models import Q
from main_app.forms import CartDetailCreationForm
import re
from .models import Tire, Cart, CartDetail
from django.forms import formset_factory, modelformset_factory

def home(req):
  return render(req, 'home.html')

def signup(req):
    if req.method == 'POST':
      form = CustomUserCreationForm(req.POST)
      if form.is_valid():
        user = form.save() # Add the user to the database
        login(req, user) #logs in on signup
        email = user.email
        #Info needed to send user email
        send_mail(
          "Thank you for registering with Road Star Tires Wholesale.",
          f"Thank you for registering {user.company_name} for an account with us. Your account will need to be verified before you can place an order, please allow us 24 business hours to do so. If this is urgent, please contact us during business hours at 111-111-1111",
          'settings.EMAIL_HOST_USER',
          [email],
          fail_silently=False
        )
        #Info needed to send admin email
        mail_admins(
          f"New signup: {user.company_name}",
          f"This user - {user.company_name}, {user.email}, {user.phone} - needs to be verified. Please log in to your admin account (http://localhost:8000/admin/login/) and verify this new user.",
          fail_silently=False
        )

        return redirect('account')
    else:
      form = CustomUserCreationForm()
    return render(req, 'signup.html', {'form': form}) # redirect to signup page

def signin(req):
  if req.user.is_authenticated:
    return redirect('tire_list')

  if req.method == 'POST':
    username = req.POST.get('username')
    password = req.POST.get('password')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
      auth.login(req, user)
      return redirect('tire_list')

    else: 
      messages.error(req, 'Wrong email/password')
  
  form = CustomUserCreationForm()
  return render(req, 'signup.html', {'form': form})

def logout(req):
  auth.logout(req)
  return render(req, 'home.html')

def account(req):
  user = req.user
  carts = Cart.objects.filter(user_id=req.user.id).order_by('-date_ordered')
  return render(req, 'account.html', { 'user': user, 'carts': carts })

def custom_user_edit(req):
  user = req.user
  form = CustomUserChangeForm(instance=user) #initiates form with user info
  if req.method == 'POST': # will only show validation errors on POST, not GET
    form = CustomUserChangeForm(req.POST, instance=user) #'instance=user' ensures you are overwriting current user and NOT creating a new one with same info
    if form.is_valid():
      user_update = form.save(commit=False)
      user_update.is_active = False # turns user to inactive and kicks them out
      form.save() # saves all the info
      # INFO NEEDED FOR EMAIL
      subject = f"{user.company_name} edited their account"
      message = f"This company - {user.company_name}, {user.email} - edited their account and will need to be re-verified. Please log in to your admin account (http://localhost:8000/admin/login/) and re-verify their account."
      mail_admins(subject, message, fail_silently=False)
      return redirect('account')
  context = {
    "form": form
  }
  return render(req, 'custom_user_edit_form.html', context)

# THIS USES DJANGO PURE FORMS AND IS LEFT IN AS AN EXAMPLE
# def custom_user_edit(request):
#   form = CustomUserEditForm() #initiates form 
#   if request.method == 'POST': # will only show validation errors on POST, not GET
#     form = CustomUserEditForm(request.POST)
#     if form.is_valid():
#       user = CustomUser(**form.cleaned_data) # uses all form data to create a user
#       user.id = request.user.id # makes sure info is tied to current user
#       user.date_joined = request.user.date_joined
#       user.discount_ratio = request.user.discount_ratio
#       user.is_active = True # turns user to inactive
#       user.is_staff = False
#       user.is_superuser = True # ONLY KEEPING FOR TESTING PURPOSES
#       user.save() # saves all the info
#   context = {
#     "form": form
#   }
#   return render(request, 'custom_user_edit_form.html', context)

def about(req):
  return render(req, 'about.html')

def services(req):
  return render(req, 'services.html')

def tires(req):
  return render(req, 'tires.html')

def cartDetail(req):
  cart = Cart.objects.filter(user_id=req.user.id, status=0).order_by('date_ordered').last()
  if cart is None:
    return render(req, 'cart.html')
  cart_details = CartDetail.objects.filter(cart_id=cart.id)
  TireFormSet = modelformset_factory(CartDetail, fields=('quantity',), extra=0)

  if req.method == 'POST':
    print(req.POST)
    formset = TireFormSet(req.POST, queryset=CartDetail.objects.filter(cart=cart))
    if formset.is_valid():
      print('valid')
      formset.save()
    else:
      print('invalid')
  
  formset = TireFormSet(queryset=CartDetail.objects.filter(cart=cart))
  zipped_data = zip(cart_details, formset)
  # return render(req, 'cart.html', {'zipped_data': zipped_data})
  return render(req, 'cart.html', {'zipped_data': zipped_data, 'formset': formset})

def removeTire(req, item_id):
  item = CartDetail.objects.get(id=item_id).delete()
  return redirect('cart_detail')

def updateTire(req, item_id):
  item = CartDetail.objects.get(id=item_id)
 
  form = CartDetailCreationForm(req.POST, instance=item)
  if form.is_valid():
    item.quantity = 10
    item.save()
  return redirect('cart_detail')

def orderDetail(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order_detail = CartDetail.objects.filter(cart_id=cart_id)
  return render(req, 'order_detail.html', { 'order': order, 'order_detail': order_detail })

def orderCancel(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order.status = 2
  order.save()
  return redirect('order_detail', cart_id)

def tireList(req):
  # tire_list = Tire.objects.all()
  # return render(req, 'tire_list.html', { 'tire_list': tire_list })
  errors = []
  if 'width' in req.GET:
    field1 = req.GET['width']
    field2 = req.GET['brand']
    field3 = req.GET['season']
    if not ((field1 or field2) or field3):
      errors.append('Enter a search term.')
    else:
      results = Tire.objects.filter(
        width__icontains=field1
      ).filter(
        brand__icontains=field2
      ).filter(
        season__icontains=field3
      )
      # query = "Field 1: %s, Field 2: %s, Field 3: %s" % (field1, field2, field3)
      return render(req, 'tire_list.html', {'tire_list': results})
  return render(req, 'tire_list.html', {'errors': errors})



def tireDetail(req, tire_id):
  # Grab a reference to the current cart, and if it doesn't exist, then create one
  # If the tire exists in the cart already, then just add the inputted quantity to the current quantity
  # If it doesn't exist in the cart, create a new instance
  tire = Tire.objects.get(pk=tire_id)
  if (Cart.objects.filter(user=req.user, status=0)).exists():
    # If for some reason there is more than one current cart, use the most recent one
    cart = Cart.objects.filter(user=req.user, status=0).order_by('date_ordered').last()
  else:
    cart = Cart.objects.create(user=req.user, status=0) # Create a current cart if it does not exist
  
  if req.method == 'POST':
    # Get the instance if it exists or create one if if doesn't
    # Returns a tuple of (object, created), where created is a boolean specifying whether an object was created
    instance, created = CartDetail.objects.get_or_create(cart=cart, tire=tire)
    if not created:
      quantityToCarry = instance.quantity # Existing cart, therefore cache the quantity to carry over
    else:
      quantityToCarry = 0 # Created cart, no value to carry over

    form = CartDetailCreationForm(req.POST, instance=instance)
    if form.is_valid():
      instance.quantity += quantityToCarry
      instance.save()

    return redirect('cart_detail')
  else:
    form = CartDetailCreationForm(
      initial = {
        'cart': cart,
        'tire': tire,
      }
    )
  return render(req, 'tire_detail.html', {'tire': tire, 'form': form})

