from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views.generic import ListView
from .models import Tire, Cart, CartDetail
from users.models import CustomUser

from .forms import CustomUserEditForm, CustomUserCreationForm

# Create your views here.

def home(req):
  return render(req, 'home.html')

def signup(req):
    if req.method == 'POST':
      form = CustomUserCreationForm(req.POST)
      if form.is_valid():
        form.save() # Add the user to the database
        #messages.success(req, 'Account created')
        return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(req, 'signup.html', {'form': form}) # redirect to signup page

def login(req):
  return render(req, 'login.html')

def account(req):
  user = req.user
  carts = Cart.objects.filter(user_id=req.user.id).order_by('-date_ordered')
  return render(req, 'account.html', { 'user': user, 'carts': carts })

def custom_user_edit(req):
  user = req.user
  form = CustomUserEditForm(instance=user) #initiates form with user info
  if req.method == 'POST': # will only show validation errors on POST, not GET
    form = CustomUserEditForm(req.POST, instance=user) #'instance=user' edits 
    if form.is_valid():
      user_update = form.save(commit=False) # uses all form data to create a user
      user_update.is_active = False # turns user to inactive and kicks them out
      #user_update.is_staff = True
      #user_update.is_superuser = True # ONLY KEEPING FOR TESTING PURPOSES
      form.save() # saves all the info
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
  return render(req, 'cart.html')

def orderDetail(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order_detail = CartDetail.objects.filter(cart_id=cart_id)
  return render(req, 'order_detail.html', { 'order': order, 'order_detail': order_detail })

def orderCancel(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order.status = 2
  order.save()
  return redirect('order_detail', cart_id)

class TireList(ListView):
  model = Tire