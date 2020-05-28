from django.urls import path, include
from . import views

urlpatterns = [
  # path('signup/', views.signup, name='signup'), # Signup page route Sign Up
  # path('login/', views.login, name='login'), # Login page route Log in vs. Sign in
  path('', views.home, name='home'), # Home page route
  # path('tires/', views.home, name='tires'), # Tire search page route - Use of collapse/accordian to display tire details?
  # path('account/<int:user_id>/', views.account, name='account'), # User account page page route

  # path('cart/<int:cart_id>/', views.cartDetail, name='cart_detail'), # Cart detail page route for current cart
  # # path('cart/<int:cart_id>/update', views.cartUpdate, name='cart_update'), # Cart update page route fort current cart (eg. for changing quantities) --> Probably not needed

  # path('orders/'), # Orders page route - List of all user's carts that have been submitted/fulfilled (ie. Cart history)
  # path('orders/<int:cart_id>/'), # Orders detail page route - Detailed view of a cart that has been submitted/fulfilled
  # path('orders/<int:cart_id>/cancel', views.cartCanceled, name='cart_cancel'), # Cart page route - Current cart
]

# Possible cart statuses: 
# current: not submitted (current cart) --> Only 1 cart has this status
# in_progress: waiting for delivery --> More than 1
# cancelled: submitted, changed mind, and then canceled --> More than 1
# fulfilled: submitted and received order --> More than 1