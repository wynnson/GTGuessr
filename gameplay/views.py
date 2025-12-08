from math import radians, sin, cos, sqrt, atan2
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from challenges.models import Challenge, HiddenChallenge
from .models import Guess

@login_required
def start_play(request):
    # Get IDs of challenges the user already guessed
    seen_ids = Guess.objects.filter(player=request.user).values_list("challenge_id", flat=True)

    # Get IDs of challenges hidden for this user (soft-hidden via report)
    hidden_ids = HiddenChallenge.objects.filter(user=request.user).values_list("challenge_id", flat=True)

    # Pick a random active challenge they haven't seen yet and isn't hidden for them
    challenge = (
        Challenge.objects.filter(is_active=True)
        .exclude(id__in=seen_ids)
        .exclude(id__in=hidden_ids)
        .order_by("?")
        .first()
    )

    if challenge:
        return redirect("gameplay.play", challenge_id=challenge.id)
    else:
        return render(
            request, "gameplay/completed.html", {
                "message": "You’ve completed all available challenges!"
            }
        )

@login_required
def play(request, challenge_id=None):
    if challenge_id:
        # If a specific challenge was requested, show it even if it's hidden globally.
        # But ensure that if the challenge is soft-hidden for this user we prevent showing it.
        challenge = get_object_or_404(Challenge, id=challenge_id)
        # If this challenge is hidden for the current user, behave as if it doesn't exist
        if HiddenChallenge.objects.filter(user=request.user, challenge=challenge).exists():
            # Redirect to start which will pick a different challenge
            return redirect('gameplay.start')
    else:
        # Find a random active challenge not hidden for this user
        hidden_ids = HiddenChallenge.objects.filter(user=request.user).values_list("challenge_id", flat=True)
        challenge = Challenge.objects.filter(is_active=True).exclude(id__in=hidden_ids).order_by("?").first()

    if request.method == "POST":
        lat_str = request.POST.get("latitude")
        lon_str = request.POST.get("longitude")
        if not lat_str or not lon_str:
            return render(request, "gameplay/play.html", {
                "challenge": challenge,
                "error": "Click on the map first.",
                "mapbox_token": settings.MAPBOX_TOKEN
            })
        lat, lon = float(lat_str), float(lon_str)
        guess = Guess.objects.create(
            player=request.user,
            challenge=challenge,
            guess_lat=lat,
            guess_lon=lon,
        )
        return redirect("gameplay.result", guess_id=guess.id)

    return render(request, "gameplay/play.html", {
        "challenge": challenge,
        "mapbox_token": settings.MAPBOX_TOKEN
    })

@login_required
def result(request, guess_id):
    """Show result after submitting a guess."""
    guess = get_object_or_404(Guess, id=guess_id, player=request.user)
    challenge = guess.challenge

    # Haversine formula
    R = 6371000
    lat1, lon1 = map(radians, [challenge.latitude, challenge.longitude])
    lat2, lon2 = map(radians, [guess.guess_lat, guess.guess_lon])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    # Scoring system: 0 meters = 1000 points, 2500+ meters = 0 points
    # Linear interpolation between these points
    if distance >= 2500:
        score = 0
    else:
        # Linear formula: score decreases linearly from 1000 at 0m to 0 at 2500m
        score = max(0, int(1000 * (1 - distance / 2500)))

    # Persist metrics on the Guess for future features (history, leaderboards)
    guess.distance_meters = float(distance)
    # time_ms can be captured client-side later; keep as-is if not provided
    # If provided via POST in future, we could set: guess.time_ms = int(request.POST.get("time_ms"))
    guess.score = score
    guess.save(update_fields=["distance_meters", "score"])

    return render(request, "gameplay/result.html", {
        "guess": guess,
        "challenge": challenge,
        "distance": round(distance, 2),
        "score": score,
        "mapbox_token": settings.MAPBOX_TOKEN,
    })


def leaderboard(request):
    User = get_user_model()
    leaderboard_entries = (
        User.objects.filter(guess__score__isnull=False)
        .annotate(
            total_points=Sum("guess__score", filter=Q(guess__score__isnull=False)),
            rounds_played=Count("guess", filter=Q(guess__score__isnull=False)),
        )
        .order_by("-total_points", "username")[:10]
    )

    return render(request, "gameplay/leaderboard.html", {
        "leaderboard": leaderboard_entries,
    })


@login_required
def history(request):
    guesses = (
        Guess.objects.filter(player=request.user, score__isnull=False)
        .select_related("challenge")
        .order_by("-created_at")
    )

    return render(request, "gameplay/history.html", {"guesses": guesses})
