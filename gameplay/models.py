from django.db import models
from django.conf import settings
from challenges.models import Challenge

class Guess(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    guess_lat = models.FloatField()
    guess_lon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Persisted gameplay metrics for future features
    distance_meters = models.FloatField(null=True, blank=True)
    time_ms = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)