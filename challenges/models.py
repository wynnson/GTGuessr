import os
from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

class Challenge(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_challenges")
    image = models.ImageField(upload_to="challenges/")
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Challenge by {self.uploader.username} ({self.created_at.date()})"

@receiver(post_delete, sender=Challenge)
def delete_challenge_image(sender, instance, **kwargs):
    """Delete file from filesystem when corresponding Challenge object is deleted."""
    if instance.image:
        image_path = instance.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)
