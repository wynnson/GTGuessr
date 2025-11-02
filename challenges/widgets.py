from django.forms import TextInput
from django.utils.safestring import mark_safe

class LeafletMapWidget(TextInput):
    template_name = "admin/leaflet_widget.html"

    class Media:
        css = {
            "all": ("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",)
        }
        js = (
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "js/admin_map.js",
        )

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        # Only insert the map once (for latitude field)
        if name == "latitude":
            html += mark_safe(
                '<div id="map" '
                'style="height:400px; margin-top:1em; border:2px solid #EAAA00; border-radius:8px;"></div>'
            )
        return mark_safe(html)
