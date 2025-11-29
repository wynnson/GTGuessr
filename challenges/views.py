from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Challenge, Report, HiddenChallenge
import os

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.heic']

@login_required
def upload_image(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        lat_str = request.POST.get("latitude")
        lon_str = request.POST.get("longitude")
        
        if not image:
            return render(request, "challenges/upload.html", {
                "error": "Please upload an image.",
                "mapbox_token": settings.MAPBOX_TOKEN
            })
            
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return render(request, "challenges/upload.html", {
                "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
                "mapbox_token": settings.MAPBOX_TOKEN
            })
            
        if not lat_str or not lon_str:
            return render(request, "challenges/upload.html", {
                "error": "Please drop a pin on the map.",
                "mapbox_token": settings.MAPBOX_TOKEN
            })
        
        lat, lon = float(lat_str), float(lon_str)
        
        Challenge.objects.create(
            uploader=request.user,
            image=image,
            latitude=float(lat),
            longitude=float(lon),
        )
        return redirect("home.index")

    # GET request, load map
    return render(request, "challenges/upload.html", {
        "mapbox_token": settings.MAPBOX_TOKEN
    })


@login_required
def report_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method != "POST":
        return redirect(reverse('gameplay.play', args=[challenge.id]))

    reason = request.POST.get('reason')
    details = request.POST.get('details', '').strip()

    if not reason:
        return redirect(f"{reverse('gameplay.play', args=[challenge.id])}?reported=0")

    Report.objects.create(
        reporter=request.user,
        challenge=challenge,
        reason=reason,
        details=details,
    )

    HiddenChallenge.objects.get_or_create(user=request.user, challenge=challenge)

    return render(request, "gameplay/removed.html", {
        "message": "This photo has been removed from your play queue. Thank you for your help.",
        "next_url": reverse('gameplay.start'),
        "challenge": challenge,
    })
