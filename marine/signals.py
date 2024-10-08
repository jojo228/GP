from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Gerant
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Gerant.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.gerant.save()
