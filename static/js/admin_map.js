document.addEventListener("DOMContentLoaded", function () {
    const latInput = document.getElementById("id_latitude");
    const lonInput = document.getElementById("id_longitude");

    if (!latInput || !lonInput) return;

    // Pull Mapbox token from the input field
    const MAPBOX_TOKEN = latInput.dataset.mapboxToken;

    // Create the map container if it doesn't exist yet
    let mapDiv = document.getElementById("map");
    if (!mapDiv) {
        mapDiv = document.createElement("div");
        mapDiv.id = "map";
        mapDiv.style.height = "400px";
        mapDiv.style.marginTop = "1em";
        mapDiv.style.border = "2px solid #EAAA00";
        mapDiv.style.borderRadius = "8px";

        lonInput.parentNode.insertAdjacentElement("afterend", mapDiv);
    }

    const defaultLat = parseFloat(latInput.value) || 33.7756;
    const defaultLon = parseFloat(lonInput.value) || -84.3963;

    const map = L.map("map").setView([defaultLat, defaultLon], 15);

    // Mapbox tile layer
    L.tileLayer(
        `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${MAPBOX_TOKEN}`,
        {
            tileSize: 512,
            zoomOffset: -1,
            attribution:
                'Mapbox | OpenStreetMap',
            maxZoom: 19,
        }
    ).addTo(map);

    let marker = null;

    if (!isNaN(defaultLat) && !isNaN(defaultLon)) {
        marker = L.marker([defaultLat, defaultLon]).addTo(map);
    }

    map.on("click", function (e) {
        const { lat, lng } = e.latlng;
        latInput.value = lat.toFixed(6);
        lonInput.value = lng.toFixed(6);

        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng).addTo(map);
        }
    });
});
