from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Profile, Transaction, BookRequest
from .tasks import send_request_approval_email

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Transaction)
def invalidate_recommendation_cache(sender, instance, **kwargs):
    cache_key = f"recommendations_{instance.user.id}"
    cache.delete(cache_key)

@receiver(post_save, sender=BookRequest)
def send_request_notification(sender, instance, created, **kwargs):
    if not created and instance.status in ['approved', 'rejected']:
        approved = instance.status == 'approved'
        send_request_approval_email.delay(instance.id, approved)
