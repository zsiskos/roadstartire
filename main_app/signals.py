import os
from django.core.mail import send_mail, mail_admins, EmailMultiAlternatives
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.template import loader
from django.utils import timezone
from email.mime.image import MIMEImage
from .models import CartDetail, Cart, OrderShipping, Tire
from django.utils import timezone

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
    order = instance.ordershipping
    cart_details = order.cart.cartdetail_set.all()
    #Info needed to send user email
    email = instance.user.email
    subject = f"Roadstar Tire Wholesale Order # {order.id} was shipped"
    message = f"Your order has been shipped and an invoice will be provided on delivery. Please log into your account to view details."
    html_message = loader.render_to_string(
      'email/invoice_email.html',
      { 'order': order,
        'user': instance.user,
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
    f = 'static/images/demo-tire-logo.png'
    fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
    msg_img = MIMEImage(fp.read())
    fp.close()
    msg_img.add_header('Content-ID', '<{}>'.format(f))
    msg.attach(msg_img)
    print(msg_img.get_filename())
    msg.send()

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
        'address_2': instance.user.address_2,
        'postal_code': instance.user.postal_code,
        'gst_number': instance.user.gst_number,
      }
    )

@receiver(post_save, sender=Tire)
def update_updated_to(sender, instance, *args, **kwargs):
  if instance.inherits_from: # If beyond the first Tire version
    Tire.objects.all().filter(id=instance.inherits_from.id).update(updated_to=instance)

@receiver(post_save, sender=Tire)
def update_date_effective(sender, instance, *args, **kwargs):
  if not instance.date_effective_tracker.has_changed('date_effective'):
    Tire.objects.all().filter(pk=instance.pk).update(date_effective = timezone.now())