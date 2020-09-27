from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
  path('signup/', views.signup, name='signup'),
  path('signup/confirmation', views.confirmation, name='confirmation'),
  path('login/', views.signin, name='login'),
  path('logout/', views.logout, name='logout'), 
  
  path('', views.home, name='home'), # Home page
  path('services/', views.services, name='services'), # Services page
  path('contact/', views.contact, name='contact'), # Contact and locations page

  path('account/', views.account, name='account'),
  path('account/edit/', views.custom_user_edit, name='custom_user_edit'), # User account page page

  path('tires/', views.tire_list, name='tire_list'), # Tire search page
  path('tires/<int:tire_id>', views.tire_detail, name='tire_detail'),

  path('add-to-cart/', views.add_to_cart, name='add_to_cart'), # Add tire to cart

  path('cart/', views.cart_detail, name='cart_detail'),
  path('cart/remove/<int:item_id>', views.remove_tire, name='remove_tire'), # Removes tire (CartDetail) from the cart
  path('cart/<int:cart_id>/order', views.cart_order, name='cart_order'), # Updates status of cart from CURRENT -> IN_PROGRESS and emails client and admin

  path('orders/<int:order_id>/', views.order_detail, name='order_detail'), # Orders detail page route - Detailed view of a cart that has been submitted, fulfilled, or cancelled
  path('orders/<int:order_id>/cancel', views.order_cancel, name='order_cancel'), # Updates Cart status from IN_PROGRESS -> CANCELLED
  path('orders/<int:order_id>/email', views.email_invoice, name='email_invoice'), # Email invoice for fulfilled orders

  # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
  path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
  path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
  path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
  path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
]