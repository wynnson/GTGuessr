from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Challenge, Report
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
                "error": "Please upload an image."
            })
            
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return render(request, "challenges/upload.html", {
                "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            })
            
        if not lat_str or not lon_str:
            return render(request, "challenges/upload.html", {
                "error": "Please drop a pin on the map."
            })
        
        lat, lon = float(lat_str), float(lon_str)
        
        Challenge.objects.create(
            uploader=request.user,
            image=image,
            latitude=float(lat),
            longitude=float(lon),
        )
        return redirect("home.index")
    return render(request, "challenges/upload.html")


@login_required
def report_challenge(request, challenge_id):
    """Handle a user report about a Challenge image.

    Expects POST with 'reason' and optional 'details'. Redirects back to the play page with
    a `reported=1` query param on success.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method != "POST":
        # Only accept POST
        return redirect(reverse('gameplay.play', args=[challenge.id]))

    reason = request.POST.get('reason')
    details = request.POST.get('details', '').strip()

    if not reason:
        # Missing reason — just redirect back
        return redirect(f"{reverse('gameplay.play', args=[challenge.id])}?reported=0")

    Report.objects.create(
        reporter=request.user,
        challenge=challenge,
        reason=reason,
        details=details,
    )

    # Redirect back to the gameplay page and indicate success
    return redirect(f"{reverse('gameplay.play', args=[challenge.id])}?reported=1")