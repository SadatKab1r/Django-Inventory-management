# inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

# Signal to create a UserProfile whenever a User is created
@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    """Create a UserProfile for the user whenever a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

# Signal to save the UserProfile whenever the User instance is saved
@receiver(post_save, sender=User)
def save_user_profile(instance, **kwargs):
    """Save the UserProfile whenever a User instance is saved."""
    instance.userprofile.save()
