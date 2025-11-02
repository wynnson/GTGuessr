from django import forms
from django.contrib import admin
from .models import Challenge
from .widgets import LeafletMapWidget

class ChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = "__all__"
        widgets = {
            "latitude": forms.TextInput(attrs={"id": "id_latitude"}),
            "longitude": forms.TextInput(attrs={"id": "id_longitude"}),
        }

    class Media:
        css = {
            "all": ("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",)
        }
        js = (
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "js/admin_map.js",
        )

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    form = ChallengeAdminForm
