from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import CartDetail

# After a Tire is removed from a Cart, if the Cart is empty, delete it
@receiver(post_delete, sender=CartDetail)
def delete_empty_cart(sender, instance, *args, **kwargs):
  print('signal fired')
  cart = instance.cart
  if not cart.cartdetail_set.all().exists():
    cart.status = -1 # 'Abandoned'
    cart.save()