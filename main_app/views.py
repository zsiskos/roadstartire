from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Tire, Cart, CartDetail

# Create your views here.

def home(req):
  return render(req, 'home.html')

def signup(req):
    #error_message = ''
    if req.method == 'POST':
        # This is how to create a 'user' form object that includes the data from the browser
        form = UserCreationForm(req.POST)
        if form.is_valid():
            user = form.save() # Add the user to the database
            login(req, user) # Log a user in via code
            return redirect('home')
    #     else:
    #         error_message = 'Invalid sign up - try again'
    # # A bad POST or a GET request, so render signup.html with an empty form
    # form = UserCreationForm()
    # context = {'form': form, 'error_message': error_message}
    # return render(req, 'registration/signup.html', context) # redirect to login page
    return render(req, 'signup.html') # redirect to login page

def login(req):
  return render(req, 'login.html')

def account(req):
  user = req.user
  orders = { 'order': Cart.objects.filter(user_id=req.user.id) }
  print(orders)
  return render(req, 'account.html', { 'user': user, 'orders': orders })

def about(req):
  return render(req, 'about.html')

def services(req):
  return render(req, 'services.html')

def tires(req):
  return render(req, 'tires.html')

def cartDetail(req):
  return render(req, 'cart.html')

def orders(req):
  return render(req, 'orders.html')