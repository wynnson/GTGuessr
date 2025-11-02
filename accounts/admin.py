from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username", "email", "role", 
        "total_score", "games_played", 
        "is_staff", "is_superuser"
    )

    fieldsets = UserAdmin.fieldsets + (
        ("GTGuessr Stats", {
            "fields": (
                "total_score",
                "games_played",
                "challenges_created",
                "best_distance_meters",
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("GTGuessr Stats", {
            "fields": (
                "total_score",
                "games_played",
                "challenges_created",
                "best_distance_meters",
            ),
        }),
    )
