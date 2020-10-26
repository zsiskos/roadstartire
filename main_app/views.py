from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, mail_admins, EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views.generic import ListView
from email.mime.image import MIMEImage
from main_app.forms import CartDetailCreationForm
from .models import Tire, Cart, CartDetail, OrderShipping
import re, os, json
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser
from django.utils import timezone

def home(req):
  user_authenticated = req.user.is_authenticated
  if (user_authenticated):
    if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
      cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
    else: 
      cart = None
    return render(req, 'home.html', {'cart': cart})
  else:
    return render(req, 'home.html')


def signup(req):
  if req.user.is_authenticated:
    return redirect('tire_list')
  if req.method == 'POST':
    form = CustomUserCreationForm(req.POST)
    if form.is_valid():
      user = form.save() # Add the user to the database
      #Info needed to send user email
      email = user.email
      subject = f"Thank you for registering with Road Star Tire Wholesale."
      message = f"Thank you for registering {user.company_name} for an account with us. Your account will need to be verified before you can log in and place an order, please allow us 24 business hours to do so. If this is urgent, please contact us during business hours at (905) 660-3209"
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
        f"This user - {user.company_name}, {user.email} - needs to be verified. Please log in to your admin account (https://demo-tire-wholesale.herokuapp.com/admin/login/) and verify this new user.",
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
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
  else: 
    cart = None
  user = req.user
  orders = OrderShipping.objects.filter(cart__user_id=req.user.id).exclude(Q(cart__status=Cart.Status.ABANDONED) | Q(cart__status=Cart.Status.CURRENT)).order_by('-cart__ordered_at')
  paginator = Paginator(orders, 5, 3) # x objects per page and y number of orphans
  page_number = req.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(req, 'account.html', {'cart': cart, 'user': user, 'orders': orders, 'page_obj': page_obj}) 

@login_required(login_url='/login')
def custom_user_edit(req):
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
  else: 
    cart = None
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
      subject = f"You have edited your Road Star Tire Wholesale account"
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
      message = f"This company - {user.company_name}, {user.email} - edited their account and will need to be re-verified. Please log in to your admin account (https://demo-tire-wholesale.herokuapp.com/admin/login/) and re-verify their account."
      mail_admins(
        subject, 
        message, 
        fail_silently=False
      )
      return redirect('account')
  return render(req, 'custom_user_edit_form.html', {'form': form, 'cart': cart})

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
  user_authenticated = req.user.is_authenticated
  if (user_authenticated):
    if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
      cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
    else: 
      cart = None
    return render(req, 'contact.html', {'cart': cart})
  else:
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
  cart = Cart.objects.get(id=cart_id)
  cart.status = Cart.Status.IN_PROGRESS
  cart_details = cart.cartdetail_set.all()
  cart.save()
  #Info needed to send user email
  email = req.user.email
  subject = f"Your order has been received - Order # {cart.ordershipping.pk}"
  message = f"Thank you for your business. Your order will be reviewed and shipped shortly. Here is a summary of your order below:"
  html_message = loader.render_to_string(
    'email/order_email.html',
    {
      'user': req.user,
      'cart': cart,
      'cart_details': cart_details
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
  # Info needed for email to admin
  subject = f"{req.user.company_name} placed Order #{cart.ordershipping.pk}"
  message = f"This company - {cart.ordershipping.company_name}, {req.user.email} - placed an order. Please log in to your admin account (https://demo-tire-wholesale.herokuapp.com/admin/login/) to view the details."
  mail_admins(
    subject, 
    message, 
    fail_silently=False
  )
  return redirect('order_detail', cart.ordershipping.pk)

def remove_tire(req, item_id):
  item = CartDetail.objects.get(id=item_id).delete()
  return redirect('cart_detail')

@login_required(login_url='/login')
def order_detail(req, order_id):
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
  else: 
    cart = None
  order = OrderShipping.objects.get(id=order_id)
  cart_details = order.cart.cartdetail_set.all()
  return render(req, 'order_detail.html', {'cart': cart, 'order': order, 'cart_details': cart_details })

def order_cancel(req, order_id):
  order = OrderShipping.objects.get(pk=order_id)
  order.cart.status = Cart.Status.CANCELLED
  order.cart.save()
  #Info needed to send user email
  email = req.user.email
  subject = f"Your order (# {order.pk}) was successfully cancelled"
  message = f"If this email is in error or if you wish to change your order, please call +1-905-660-3209."
  send_mail(
    subject, 
    message, 
    'settings.EMAIL_HOST_USER', 
    [email], 
    fail_silently=False
  )
  # Info needed for email to admin
  user = req.user
  subject = f"{user.company_name} cancelled order #{order.pk}"
  message = f"This company - {user.company_name}, {user.email} - cancelled an order. Please log in to your admin account (https://demo-tire-wholesale.herokuapp.com/admin/login/) to view the details."
  mail_admins(
    subject, 
    message, 
    fail_silently=False
  )
  return redirect('order_detail', order.pk)

# Uses a different email method so that images can be attached
def email_invoice(req, order_id):
  order = OrderShipping.objects.get(id=order_id)
  cart_details = order.cart.cartdetail_set.all()
  #Info needed to send user email
  email = req.user.email
  subject = f"ORDER INVOICE"
  message = f"Your order has been shipped and an invoice will be provided on delivery. Please log into your account to view details."
  html_message = loader.render_to_string(
    'email/invoice_email.html',
    { 'order': order,
      'user': req.user,
      'cart_details': cart_details
    })
  msg = EmailMultiAlternatives(
    subject, 
    message, 
    'settings.EMAIL_HOST_USER', 
    [email]
  )
  msg.attach_alternative(html_message, "text/html")
  msg.mixed_subtype = 'related'
  f = 'static/images/road-star-logo.png'
  fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
  msg_img = MIMEImage(fp.read())
  fp.close()
  msg_img.add_header('Content-ID', '<{}>'.format(f))
  msg.attach(msg_img)
  msg.send()
  return redirect('account')

@login_required(login_url='/login')
def tire_list(req):
  
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
  else: 
    cart = None

  sort = None

  if 'quick_search' in req.GET:
    if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
      cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
    else: 
      cart = None

    quick_search = req.GET['quick_search']
    cleaned_query = re.sub('\D', '', quick_search)
    width = cleaned_query[:3]
    aspect_ratio = cleaned_query[3:5]
    rim_size = cleaned_query[-2:]
    result = Tire.objects.filter(
        updated_to=None
      ).filter(
        width__icontains=width
      ).filter(
        aspect_ratio__icontains=aspect_ratio
      ).filter(
        rim_size__icontains=rim_size
      )

    sort = req.GET.get('sort', '')

    if not quick_search:
      results = Tire.objects.filter(updated_to=None).order_by('price')
      if sort:
        results = result.filter(updated_to=None).order_by(sort)
    else:
      results = result.order_by('price')
      if sort:
        results = result.filter(updated_to=None).order_by(sort)

    paginator = Paginator(results, 20) # x objects per page and y number of orphans
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(req, 'tire_list.html', {'sort': sort, 'cart': cart, 'results' : results, 'page_obj' : page_obj})

  if 'width' in req.GET:
    if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
      cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)
    else: 
      cart = None
    width = req.GET['width']
    aspect_ratio = req.GET['aspect_ratio']
    rim_size = req.GET['rim_size']
    brand = req.GET['brand']
    tire_type = req.GET['tire_type']
    result = Tire.objects.filter(
        updated_to=None
      ).filter(
        width__icontains=width
      ).filter(
        aspect_ratio__icontains=aspect_ratio
      ).filter(
        rim_size__icontains=rim_size
      ).filter(
        brand__icontains=brand
      ).filter(
        tire_type__icontains=tire_type
      )

    sort = req.GET.get('sort', '')

    if not (width or aspect_ratio or tire_type or brand or rim_size):
      results = Tire.objects.filter(updated_to=None).order_by('price')
      if sort:
        results = result.order_by(sort)
    else:
      results = result.order_by('price')
      if sort:
        results = result.order_by(sort)

    paginator = Paginator(results, 20) # x objects per page and y number of orphans
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(req, 'tire_list.html', {'sort': sort, 'cart' : cart, 'results' : results, 'page_obj' : page_obj, 'paginator': paginator})
  return render(req, 'tire_list.html', {'cart': cart})

def tire_detail(req, tire_id):
  # Grab a reference to the current cart, and if it doesn't exist, then create one
  # If the tire exists in the cart already, then just add the inputted quantity to the current quantity
  # If it doesn't exist in the cart, create a new instance
  tire = Tire.objects.get(pk=tire_id)
  updated_tire = tire.get_updated_tire()
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    # If for some reason there is more than one current cart, use the most recent one
    cart = Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT).order_by('ordered_at').last()
  else:
    cart = Cart.objects.create(user=req.user, status=Cart.Status.CURRENT) # Create a current cart if it does not exist
  
  if req.method == 'POST':
    # Get the instance if it exists or create one if if doesn't
    # Returns a tuple of (object, created), where created is a boolean specifying whether an object was created
    instance, created = CartDetail.objects.get_or_create(cart=cart, product=updated_tire.product)
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
  return render(req, 'tire_detail.html', {'cart': cart, 'tire': updated_tire, 'form': form})

@login_required(login_url='/login')
# @api_view(['POST'])
def add_to_cart(req):
  body = json.loads(req.body)

  tire = Tire.objects.get(pk=body["id"])
  if (Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT)).exists():
    # If for some reason there is more than one current cart, use the most recent one
    cart = Cart.objects.filter(user=req.user, status=Cart.Status.CURRENT).order_by('ordered_at').last()
  else:
    cart = Cart.objects.create(user=req.user, status=Cart.Status.CURRENT) # Create a current cart if it does not exist

  form = CartDetailCreationForm(
    initial = {
      'cart': cart,
      'tire': tire,
    }
  )

  instance, created = CartDetail.objects.get_or_create(cart=cart, product=tire.product)
  if not created:
    quantityToCarry = instance.quantity # Existing cart, therefore cache the quantity to carry over
  else:
    quantityToCarry = instance.quantity - 1 # Created cart, no value to carry over
  instance.quantity = int(body["quantity"]) + quantityToCarry
  instance.save()
  # cart = Cart.objects.get(user=req.user, status=Cart.Status.CURRENT)

  return JsonResponse({})
