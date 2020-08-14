from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from .models import CartDetail, Cart, OrderShipping
from django.utils import timezone
from django.core.mail import send_mail, mail_admins
from users.models import CustomUser

# After a CartDetail is deleted, if the Cart no longer has CartDetail objects associated with it (ie. the Cart is now empty), mark the Cart as 'ABANDONED'
@receiver(post_delete, sender=CartDetail)
def delete_empty_cart(sender, instance, *args, **kwargs):
  cart = instance.cart
  if not cart.cartdetail_set.all().exists():
    cart.status = cart.Status.ABANDONED
    cart.save()

@receiver(pre_save, sender=Cart)
def update_cart_time_metadata(sender, instance, *args, **kwargs):
  if instance.status_tracker.has_changed('status'):
    # ... --> IN_PROGRESS:
    if instance.status == Cart.Status.IN_PROGRESS:
      instance.closed_at = None
      instance.ordered_at = timezone.now()
    # ─────────────────────────────────────────────────────────────────
    # ... --> FULFILLED / CANCELLED / ABANDONED
    elif instance.status == Cart.Status.FULFILLED or instance.status == Cart.Status.CANCELLED or instance.status == Cart.Status.ABANDONED:
      instance.closed_at = timezone.now()
      if instance.status == Cart.Status.FULFILLED and instance.ordered_at is None:
        instance.ordered_at = timezone.now()
    # ─────────────────────────────────────────────────────────────────
    # ... --> CURRENT
    elif instance.status == Cart.Status.CURRENT:
      instance.ordered_at = None
      instance.closed_at = None

# Send email confirmation to client when their order is marked as fulfilled
@receiver(post_save, sender=Cart)
def send_order_fulfilled_email(sender, instance, *args, **kwargs):
  if instance.status_tracker.has_changed('status') and instance.status == Cart.Status.FULFILLED:
    email = instance.user.email
    subject = f"Your order (# {instance.ordershipping.pk}) has been fulfilled"
    message = f"This is an email confirmation to let you know that your order (# {instance.ordershipping.pk}) totalling ${instance.get_total()} has been successfully fulfilled. Thank you for your business!"
    send_mail(
      subject, 
      message, 
      'settings.EMAIL_HOST_USER', 
      [email], 
      fail_silently=False
    )

# When an order is placed, create a OrderShipping object that saves the user's current shipping info defined on their profile
@receiver(post_save, sender=Cart)
def create_order_shipping(sender, instance, *args, **kwargs):
  if not Cart.does_state_require_shipping_info(instance.status_tracker.previous('status')) and Cart.does_state_require_shipping_info(instance.status):
    obj, created = OrderShipping.objects.get_or_create(
      cart = instance,
      defaults = {
        'first_name': instance.user.first_name,
        'last_name': instance.user.last_name,
        'company_name': instance.user.company_name,
        'business_phone': instance.user.business_phone,
        'country_iso': instance.user.country_iso,
        'province_iso': instance.user.province_iso,
        'city': instance.user.city,
        'address': instance.user.address,
        'postal_code': instance.user.postal_code,
        'hst_number': instance.user.hst_number,
      }
    )