from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ("player", "Player"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="player")
    total_score = models.IntegerField(default=0)
    games_played = models.PositiveIntegerField(default=0)
    challenges_created = models.PositiveIntegerField(default=0)
    best_distance_meters = models.FloatField(null=True, blank=True)
    join_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def average_score(self):
        """Average score per game, or 0 if none played."""
        return self.total_score / self.games_played if self.games_played else 0
