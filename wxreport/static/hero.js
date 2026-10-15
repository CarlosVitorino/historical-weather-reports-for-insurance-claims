/* Landing page map: the real records from the sample report, on a muted street map. */
(function () {
  "use strict";
  var el = document.getElementById("hero-map");
  if (!el || !window.L) return;
  var map = L.map(el, {
    zoomControl: false, dragging: false, scrollWheelZoom: false, doubleClickZoom: false,
    boxZoom: false, keyboard: false, touchZoom: false, tap: false, attributionControl: true
  });
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  function square(color) {
    return L.divIcon({ className: "", iconSize: [14, 14], iconAnchor: [7, 7],
      html: '<div style="width:14px;height:14px;border-radius:3px;background:' + color +
            ';border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div>' });
  }
  function diamond() {
    return L.divIcon({ className: "", iconSize: [10, 10], iconAnchor: [5, 5],
      html: '<div style="width:9px;height:9px;background:#3d7fc2;transform:rotate(45deg);border:1px solid #fff"></div>' });
  }
  function pin() {
    return L.divIcon({ className: "", iconSize: [22, 22], iconAnchor: [11, 26], html: '<div class="pin"></div>' });
  }

  fetch(el.dataset.src).then(function (r) { return r.json(); }).then(function (d) {
    var site = L.latLng(d.site[0], d.site[1]);
    var miles = 6.5, dLat = miles / 69, dLon = miles / (69.17 * Math.cos(site.lat * Math.PI / 180));
    map.fitBounds([[site.lat - dLat, site.lng - dLon], [site.lat + dLat, site.lng + dLon]]);

    d.warnings.forEach(function (poly) {
      L.polygon(poly, { color: "#d68f1f", weight: 2, dashArray: "6 5", fillColor: "#f2a93b", fillOpacity: 0.12,
                        interactive: false }).addTo(map);
    });
    d.radar_hail.forEach(function (h) {
      L.circleMarker([h[0], h[1]], { radius: 3 + 2.4 * h[2], color: "#3d7fc2", weight: 1, fillColor: "#3d7fc2",
                                     fillOpacity: 0.22, interactive: false }).addTo(map);
    });
    d.hail_reports.forEach(function (h) { L.marker(h, { icon: diamond(), interactive: false }).addTo(map); });

    L.polyline(d.tornado.path, { color: "#d9442e", weight: 6, opacity: 0.9, lineCap: "round", interactive: false })
      .addTo(map)
      .bindTooltip(d.tornado.scale + " tornado path", { permanent: true, direction: "left", offset: [-10, 0] });
    L.marker(d.station.at, { icon: square("#12263f") }).addTo(map)
      .bindTooltip(d.station.gust_mph + " mph gust · " + d.station.name, { permanent: true, direction: "bottom",
        offset: [0, 10] });
    L.marker(site, { icon: pin(), zIndexOffset: 1000 }).addTo(map)
      .bindTooltip("The property", { permanent: true, direction: "right", offset: [12, -12] });
  }).catch(function () { /* the findings below the map still tell the story */ });
})();
