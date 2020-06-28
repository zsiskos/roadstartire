from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import CartDetail

# After a CartDetail is deleted, if the Cart no longer has CartDetail objects associated with it (ie. the Cart is now empty), mark the Cart as 'ABANDONED'
@receiver(post_delete, sender=CartDetail)
def delete_empty_cart(sender, instance, *args, **kwargs):
  print('signal fired')
  cart = instance.cart
  if not cart.cartdetail_set.all().exists():
    cart.status = cart.Status.ABANDONED
    cart.save()