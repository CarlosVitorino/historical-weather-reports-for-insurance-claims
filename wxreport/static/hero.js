/* Landing page: page 1 of the sample report as a live map (same records, extent and rings as the PDF). */
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

  function icon(html, size) {
    return L.divIcon({ className: "", iconSize: [size, size], iconAnchor: [size / 2, size / 2], html: html });
  }
  var MARK = {
    hail: '<div style="width:9px;height:9px;background:#3d7fc2;transform:rotate(45deg);border:1px solid #fff"></div>',
    wind: '<div style="width:9px;height:9px;border-radius:50%;background:#6b4fa0;border:1px solid #fff"></div>',
    tornado: '<div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;' +
             'border-bottom:10px solid #d9442e"></div>'
  };
  var MILE = 1609.344;

  fetch(el.dataset.src).then(function (r) { return r.json(); }).then(function (d) {
    var site = L.latLng(d.site[0], d.site[1]);
    function fit() {
      var r = d.radius_mi * MILE;
      map.fitBounds(L.latLng(site).toBounds(2 * r), { padding: [6, 6] });
    }
    fit();
    new ResizeObserver(function () { map.invalidateSize(); fit(); }).observe(el);

    d.warnings.forEach(function (poly) {
      L.polygon(poly, { color: "#c9821a", weight: 1.6, dashArray: "6 5", fillColor: "#f2a93b", fillOpacity: 0.13,
                        interactive: false }).addTo(map);
    });
    for (var r = d.ring_step; r <= d.radius_mi + 1e-6; r += d.ring_step) {
      L.circle(site, { radius: r * MILE, color: "#4b5868", weight: 0.8, opacity: 0.55, fill: false, interactive: false })
        .addTo(map);
      var at = L.latLng(site.lat + (r / 69) * Math.sin(Math.PI / 3),
                        site.lng + (r / (69.17 * Math.cos(site.lat * Math.PI / 180))) * Math.cos(Math.PI / 3));
      L.marker(at, { interactive: false, icon: L.divIcon({ className: "", iconSize: [34, 14], iconAnchor: [0, 7],
        html: '<span style="font:500 10px Geist,sans-serif;color:#5d6b7c;background:rgba(255,255,255,.85);' +
              'padding:0 3px;border-radius:3px">' + r + ' mi</span>' }) }).addTo(map);
    }
    d.radar_hail.forEach(function (h) {
      L.circleMarker([h[0], h[1]], { radius: 3 + 2.2 * h[2], color: "#3d7fc2", weight: 1, fillColor: "#3d7fc2",
                                     fillOpacity: 0.22, interactive: false }).addTo(map);
    });
    d.tornado_paths.forEach(function (p) {
      L.polyline(p, { color: "#d9442e", weight: 5, opacity: 0.95, lineCap: "round", interactive: false }).addTo(map);
    });
    d.reports.forEach(function (rep) {
      if (MARK[rep[2]]) L.marker([rep[0], rep[1]], { icon: icon(MARK[rep[2]], 12), interactive: false }).addTo(map);
    });
    d.stations.forEach(function (s) {
      L.marker(s.at, { icon: icon('<div style="width:11px;height:11px;border-radius:2px;background:#12263f;' +
                                  'border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.35)"></div>', 15) })
        .addTo(map).bindTooltip(s.name, { permanent: true, direction: "right", offset: [8, 0], className: "st" });
    });
    L.marker(site, { zIndexOffset: 1000, icon: icon(
      '<div style="width:13px;height:13px;border-radius:50%;background:#f2a93b;border:3px solid #0b1a2e;' +
      'box-shadow:0 0 0 7px rgba(242,169,59,.3)"></div>', 19) })
      .addTo(map).bindTooltip("Property", { permanent: true, direction: "right", offset: [12, -8] });
  }).catch(function () { /* the key facts below the map still tell the story */ });
})();
