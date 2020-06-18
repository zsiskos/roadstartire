from django.urls import path, include
from . import views

urlpatterns = [
  path('signup/', views.signup, name='signup'), # Signup page route Sign Up
  path('login/', views.signin, name='login'), # Login page route Log in vs. Sign in, creating separate template for this for now until we combine it with signup page
  path('logout/', views.logout, name='logout'), 
  
  path('', views.home, name='home'), # Home page route
  path('services/', views.services, name='services'), #Services page route
  path('about/', views.about, name='about'), #About and Locations page route

  path('account/', views.account, name='account'), #Temporary route page until we set up the model
  path('account/edit/', views.custom_user_edit, name='custom_user_edit'), # User account page page route

  path('tires/', views.tireList, name='tire_list'), # Tire search page route - Use of collapse/accordian to display tire details?
  # path('tires/', views.TireList.as_view(), name='tire_list'),
  path('tires/<int:tire_id>', views.tireDetail, name='tire_detail'),

  path('cart/', views.cartDetail, name='cart_detail'), # Temporary path until we set up the cart model
  path('cart/remove/<int:item_id>', views.removeTire, name='remove_tire'),
  path('cart/update/<int:item_id>', views.updateTire, name='update_tire'),
  # path('cart/<int:cart_id>/', views.cartDetail, name='cart_detail'), # Cart detail page route for current cart
  # path('cart/<int:cart_id>/update', views.cartUpdate, name='cart_update'), # Cart update page route fort current cart (eg. for changing quantities) --> Probably not needed

  path('orders/<int:cart_id>/', views.orderDetail, name='order_detail'), # Orders detail page route - Detailed view of a cart that has been submitted/fulfilled
  path('orders/<int:cart_id>/cancel', views.orderCancel, name='order_cancel'), # Cart page route - Current cart
]

# Possible cart statuses: 
# current: not submitted (current cart) --> Only 1 cart has this status
# in_progress: waiting for delivery --> More than 1
# cancelled: submitted, changed mind, and then canceled --> More than 1
# fulfilled: submitted and received order --> More than 1