from django.conf import settings
from django.shortcuts import render

def index(request):
    return render(request, "home/index.html", {
        "mapbox_token": settings.MAPBOX_TOKEN
    })