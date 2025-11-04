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


class Report(models.Model):
    REASON_CHOICES = [
        ("inaccurate", "Inaccurate location"),
        ("inappropriate", "Inappropriate content"),
        ("spam", "Spam / Duplicate"),
        ("other", "Other"),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=32, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report({self.get_reason_display()}) by {self.reporter.username} on Challenge {self.challenge.id}"


class HiddenChallenge(models.Model):
    """
    keeps the Challenge active in the system for others but excludes it
    from the reporting user's future play queue until an admin acts.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hidden_challenges")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="hidden_for")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user', 'challenge'),)

    def __str__(self):
        return f"HiddenChallenge(user={self.user.username}, challenge={self.challenge.id})"
