from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
  path('signup/', views.signup, name='signup'), # Signup page route Sign Up
  path('signup/confirmation', views.confirmation, name='confirmation'), #Confirmation page after signing up
  path('login/', views.signin, name='login'), # Login page route 
  path('logout/', views.logout, name='logout'), 
  
  path('', views.home, name='home'), # Home page route
  path('services/', views.services, name='services'), #Services page route
  path('contact/', views.contact, name='contact'), #Contact and Locations page route

  path('account/', views.account, name='account'), #Temporary route page until we set up the model
  path('account/edit/', views.custom_user_edit, name='custom_user_edit'), # User account page page route

  path('tires/', views.tire_list, name='tire_list'), # Tire search page route - Use of collapse/accordian to display tire details?
  path('tires/<int:tire_id>', views.tire_detail, name='tire_detail'),

  path('cart/', views.cart_detail, name='cart_detail'), # Temporary path until we set up the cart model
  path('cart/remove/<int:item_id>', views.remove_tire, name='remove_tire'), #Removes tire (cartDetail) from the cart
  path('cart/<int:cart_id>/order', views.cart_order, name='cart_order'), #Changes status of cart and notifies admin

  path('orders/<int:cart_id>/', views.order_detail, name='order_detail'), # Orders detail page route - Detailed view of a cart that has been submitted/fulfilled
  path('orders/<int:cart_id>/cancel', views.order_cancel, name='order_cancel'), # cancels inprogress cart
  path('orders/<int:cart_id>/email', views.email_invoice, name='email_invoice'), # Eamil invoice for fulfilled orders

  # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
  path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
  path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
  path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
  path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
]

# Possible cart statuses: 
# current: not submitted (current cart) --> Only 1 cart has this status
# in_progress: waiting for delivery --> More than 1
# cancelled: submitted, changed mind, and then canceled --> More than 1
# fulfilled: submitted and received order --> More than 1