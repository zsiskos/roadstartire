import os
from django.core.mail import send_mail, mail_admins, EmailMultiAlternatives
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.template import loader
from django.utils import timezone
from email.mime.image import MIMEImage
from .models import CartDetail, Cart

# After a CartDetail is deleted, if the Cart no longer has CartDetail objects associated with it (ie. the Cart is now empty), mark the Cart as 'ABANDONED'
@receiver(post_delete, sender=CartDetail)
def delete_empty_cart(sender, instance, *args, **kwargs):
  cart = instance.cart
  if not cart.cartdetail_set.all().exists():
    cart.status = cart.Status.ABANDONED
    cart.save()

@receiver(pre_save, sender=Cart)
def update_closed_at(sender, instance, *args, **kwargs):
  if instance.status_tracker.has_changed('status'):
    # ... --> IN_PROGRESS:
    if instance.status == Cart.Status.IN_PROGRESS:
      instance.closed_at = None
      instance.ordered_at = timezone.now()
    # ─────────────────────────────────────────────────────────────────
    # ... --> FULFILLED / CANCELLED / ABANDONED
    elif instance.status == Cart.Status.FULFILLED or instance.status == Cart.Status.CANCELLED or instance.status == Cart.Status.ABANDONED:
      instance.closed_at = timezone.now()
      
      if instance.status == Cart.Status.FULFILLED:
        email = instance.user.email
        order = instance
        order_detail = instance.cartdetail_set.all()
        subject = f"Order # {instance.pk} has been shipped"
        message = f"This is an email confirmation to let you know that your order (# {instance.pk}) totalling ${instance.get_total()} has been shipped. Thank you for your business!"
        html_message = loader.render_to_string(
          'email/invoice_email.html',
          { 'order': order,
            'user': instance.user,
            'order_detail': order_detail
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
        print(msg_img.get_filename())
        msg.send()
    # ─────────────────────────────────────────────────────────────────
    # ... --> CURRENT
    elif instance.status == Cart.Status.CURRENT:
      instance.ordered_at = None
      instance.closed_at = None