from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Challenge
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