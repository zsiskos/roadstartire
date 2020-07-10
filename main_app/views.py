from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, mail_admins
from django.db.models import Q
from django.forms import formset_factory, modelformset_factory
from django.shortcuts import render, redirect
from django.views.generic import ListView
from main_app.forms import CartDetailCreationForm
from .models import Tire, Cart, CartDetail
import re
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser
from django.core.paginator import Paginator
from django.template import loader

def home(req):
  return render(req, 'home.html')

def signup(req):
    if req.method == 'POST':
      form = CustomUserCreationForm(req.POST)
      if form.is_valid():
        user = form.save() # Add the user to the database
        #Info needed to send user email
        email = user.email
        subject = f"Thank you for registering with Road Star Tires Wholesale."
        message = f"Thank you for registering {user.company_name} for an account with us. Your account will need to be verified before you can place an order, please allow us 24 business hours to do so. If this is urgent, please contact us during business hours at 111-111-1111"
        send_mail(
          subject, 
          message, 
          'settings.EMAIL_HOST_USER', 
          [email], 
          fail_silently=False
        )
        #Info needed to send admin email
        mail_admins(
          f"New signup: {user.company_name}",
          f"This user - {user.company_name}, {user.email} - needs to be verified. Please log in to your admin account (http://localhost:8000/admin/login/) and verify this new user.",
          fail_silently=False
        )
        return redirect('confirmation')
    else:
      form = CustomUserCreationForm()
    return render(req, 'signup.html', {'form': form}) # redirect to signup page

def confirmation(req):
  return render(req, 'confirmation.html')


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
  return render(req, 'login.html', {'form': form})

def logout(req):
  auth.logout(req)
  return render(req, 'home.html')

@login_required(login_url='/login')
def account(req):
  user = req.user
  carts = Cart.objects.filter(user_id=req.user.id).exclude(Q(status=Cart.Status.ABANDONED) | Q(status=Cart.Status.CURRENT)).order_by('-ordered_at')

  paginator = Paginator(carts, 5, 3) # x objects per page and y number of orphans
  page_number = req.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(req, 'account.html', {'user': user, 'carts': carts, 'page_obj': page_obj})

  # return render(req, 'account.html', { 'user': user, 'carts': carts })

@login_required(login_url='/login')
def custom_user_edit(req):
  user = req.user
  form = CustomUserChangeForm(instance=user) #initiates form with user info
  if req.method == 'POST': # will only show validation errors on POST, not GET
    form = CustomUserChangeForm(req.POST, instance=user) #'instance=user' ensures you are overwriting current user and NOT creating a new one with same info
    if form.is_valid():
      user_update = form.save(commit=False)
      user_update.is_active = False # turns user to inactive and kicks them out
      form.save() # saves all the info
      #Info needed to send user email
      email = req.user.email
      subject = f"You have edited your Road Star Tire Wholesale account."
      message = f"A Road Star Tire staff member will have to re-verify your account before you can log in again to place an order. If this is an error or urgent, please call +1-905-660-3209."
      send_mail(
        subject, 
        message, 
        'settings.EMAIL_HOST_USER', 
        [email], 
        fail_silently=False
      )
      # INFO NEEDED FOR EMAIL
      subject = f"{user.company_name} edited their account"
      message = f"This company - {user.company_name}, {user.email} - edited their account and will need to be re-verified. Please log in to your admin account (http://localhost:8000/admin/login/) and re-verify their account."
      mail_admins(
        subject, 
        message, 
        fail_silently=False
      )
      return redirect('account')
  return render(req, 'custom_user_edit_form.html', {'form': form})

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

def contact(req):
  return render(req, 'contact.html')

def services(req):
  return render(req, 'services.html')

@login_required(login_url='/login')
def cart_detail(req):
  try:
    cart = Cart.objects.get(user_id=req.user.id, status=Cart.Status.CURRENT)
  except Cart.DoesNotExist:
    return render(req, 'cart.html')
  cart_details = cart.cartdetail_set.all().order_by('created_at') # Need to order for front-end to render properly after updating the quantity
  TireFormSet = modelformset_factory(CartDetail, fields=('quantity',), extra=0)
  if req.method == 'POST':
    formset = TireFormSet(req.POST, req.FILES, queryset=cart_details)
    # if formset.is_valid(): TOOK OUT BUT NOT SURE WHY IT DOESN"T WORK WITH IT IN
    formset.save()
    return redirect('cart_detail')
  formset = TireFormSet(queryset=cart_details)
  zipped_data = zip(cart_details, formset)
  return render(req, 'cart.html', {'cart': cart, 'zipped_data': zipped_data, 'formset': formset})

@login_required(login_url='/login')
def cart_order(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order.status = Cart.Status.IN_PROGRESS
  order_detail = order.cartdetail_set.all()
  order.save()
  #Info needed to send user email
  email = req.user.email
  subject = f"Thank you for ordering with Road Star Tires Wholesale."
  message = f"Thank you for placing your order. A Road Star Tire staff member has been notified about your order and will be in touch regarding delivery details. If you need to contact us before then, please call +1-905-660-3209."
  html_message = loader.render_to_string(
    'email/order_email.html',
    { 'order': order,
      'user': req.user,
      'order_detail': order_detail
    }
  )
  send_mail(
    subject, 
    message, 
    'settings.EMAIL_HOST_USER', 
    [email], 
    fail_silently=False,
    html_message=html_message
  )
  # INFO NEEDED FOR EMAIL
  user = req.user
  subject = f"{user.company_name} placed Order #{order.id}"
  message = f"This company - {user.company_name}, {user.email} - placed an order. Please log in to your admin account (http://localhost:8000/admin/login/) to view the details."
  mail_admins(
    subject, 
    message, 
    fail_silently=False
  )
  return redirect('order_detail', cart_id)

def remove_tire(req, item_id):
  item = CartDetail.objects.get(id=item_id).delete()
  return redirect('cart_detail')

@login_required(login_url='/login')
def order_detail(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order_detail = CartDetail.objects.filter(cart_id=cart_id)
  return render(req, 'order_detail.html', { 'order': order, 'order_detail': order_detail })

def order_cancel(req, cart_id):
  order = Cart.objects.get(id=cart_id)
  order.status = Cart.Status.CANCELLED
  order.save()
  #Info needed to send user email
  email = req.user.email
  subject = f"You have cancelled Order #{order.id}."
  message = f"If this email is in error or if you wish to change your order, please call +1-905-660-3209."
  send_mail(
    subject, 
    message, 
    'settings.EMAIL_HOST_USER', 
    [email], 
    fail_silently=False
  )
  # INFO NEEDED FOR EMAIL
  user = req.user
  subject = f"{user.company_name} cancelled order #{order.id}"
  message = f"This company - {user.company_name}, {user.email} - cancelled an order. Please log in to your admin account (http://localhost:8000/admin/login/) to view the details."
  mail_admins(
    subject, 
    message, 
    fail_silently=False
  )
  return redirect('order_detail', cart_id)

@login_required(login_url='/login')
def tire_list(req):
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

def tire_detail(req, tire_id):
  # Grab a reference to the current cart, and if it doesn't exist, then create one
  # If the tire exists in the cart already, then just add the inputted quantity to the current quantity
  # If it doesn't exist in the cart, create a new instance
  tire = Tire.objects.get(pk=tire_id)
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    # If for some reason there is more than one current cart, use the most recent one
    cart = Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT).order_by('ordered_at').last()
  else:
    cart = Cart.objects.create(user=req.user, status=Cart.Status.CURRENT) # Create a current cart if it does not exist
  
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

