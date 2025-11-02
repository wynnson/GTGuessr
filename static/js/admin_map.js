window.addEventListener("load", () => {
  const latInput = document.getElementById("id_latitude");
  const lonInput = document.getElementById("id_longitude");

  // stop if fields not present
  if (!latInput || !lonInput) return;

  // create map container dynamically after longitude field
  const mapDiv = document.createElement("div");
  mapDiv.id = "map";
  mapDiv.style.height = "400px";
  mapDiv.style.marginTop = "1em";
  mapDiv.style.border = "2px solid #EAAA00"; // GT gold border
  mapDiv.style.borderRadius = "8px";
  lonInput.parentNode.insertAdjacentElement("afterend", mapDiv);

  // extract current coordinates or default to GT center
  const defaultLat = parseFloat(latInput.value) || 33.7756;
  const defaultLon = parseFloat(lonInput.value) || -84.3963;

  // wait until map div exists
  requestAnimationFrame(() => {
    // initialize leaflet map
    const map = L.map("map").setView([defaultLat, defaultLon], 15);

    // add base tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    let marker = null;

    // if lat/lon already set, show existing marker (edit mode)
    if (!isNaN(defaultLat) && !isNaN(defaultLon) &&
        latInput.value && lonInput.value) {
      marker = L.marker([defaultLat, defaultLon]).addTo(map);
      map.setView([defaultLat, defaultLon], 16);
    }

    // update coords when clicking map
    map.on("click", function (e) {
      const { lat, lng } = e.latlng;
      latInput.value = lat.toFixed(6);
      lonInput.value = lng.toFixed(6);

      if (marker) map.removeLayer(marker);
      marker = L.marker([lat, lng]).addTo(map);
    });
  });
});
