from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from .models import CartDetail, Cart
from django.utils import timezone

# After a CartDetail is deleted, if the Cart no longer has CartDetail objects associated with it (ie. the Cart is now empty), mark the Cart as 'ABANDONED'
@receiver(post_delete, sender=CartDetail)
def delete_empty_cart(sender, instance, *args, **kwargs):
  cart = instance.cart
  if not cart.cartdetail_set.all().exists():
    cart.status = cart.Status.ABANDONED
    cart.save()

@receiver(pre_save, sender=Cart)
def update_fulfilled_at(sender, instance, *args, **kwargs):
  if instance.status_tracker.has_changed('status'):
    # ... --> IN_PROGRESS:
    if instance.status == Cart.Status.IN_PROGRESS:
      instance.fulfilled_at = None
      instance.ordered_at = timezone.now()
    # ... --> FULFILLED:
    elif instance.status == Cart.Status.FULFILLED:
      if instance.ordered_at is None:
        instance.ordered_at = timezone.now()
      instance.fulfilled_at = timezone.now()
    # ... --> CANCELLED
    elif instance.status == Cart.Status.CANCELLED:
      if instance.ordered_at is None:
        instance.ordered_at = timezone.now()
      instance.fulfilled_at = None
    # ... --> CURRENT/ABANDONED
    elif instance.status == Cart.Status.CURRENT or instance.status == Cart.Status.ABANDONED:
      instance.ordered_at = None
      instance.fulfilled_at = None