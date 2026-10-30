/* Storm Reports: a storm's reports on a map (hail diamonds, wind dots, tornado paths), with the city centre and the
   circle the city page covers. storm-city.js calls window.stormMap again when another storm day is picked. */
(function () {
  "use strict";
  var MARK = {
    hail: '<div style="width:10px;height:10px;background:#3d7fc2;transform:rotate(45deg);border:1px solid #fff"></div>',
    wind: '<div style="width:10px;height:10px;border-radius:50%;background:#6b4fa0;border:1px solid #fff"></div>',
    tornado: '<div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;' +
             'border-bottom:12px solid #d9442e"></div>'
  };
  var current = null;

  function icon(html, size) {
    return L.divIcon({ className: "", iconSize: [size, size], iconAnchor: [size / 2, size / 2], html: html });
  }

  function draw(el) {
    if (!el || !window.L) return;
    if (current) { current.remove(); current = null; }
    var d = JSON.parse(el.dataset.storm);
    var map = L.map(el, { scrollWheelZoom: false });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
    var bounds = [];

    if (d.center) {
      var c = L.latLng(d.center[0], d.center[1]);
      L.circle(c, { radius: d.ring_mi * 1609.344, color: "#4b5868", weight: 1, opacity: 0.6, dashArray: "5 5",
                    fill: false, interactive: false }).addTo(map);
      L.marker(c, { zIndexOffset: 1000, interactive: false, icon: icon(
        '<div style="width:12px;height:12px;border-radius:50%;background:#f2a93b;border:3px solid #0b1a2e"></div>', 18) })
        .addTo(map).bindTooltip(d.center[2], { permanent: true, direction: "right", offset: [10, 0] });
      // The circle's extent, worked out directly: Leaflet can only measure it once the map has a view.
      var dLat = d.ring_mi / 69.0, dLon = d.ring_mi / (69.17 * Math.cos(c.lat * Math.PI / 180));
      bounds.push([c.lat - dLat, c.lng - dLon], [c.lat + dLat, c.lng + dLon]);
    }
    d.paths.forEach(function (p) {
      L.polyline(p, { color: "#d9442e", weight: 5, opacity: 0.9, lineCap: "round" }).addTo(map);
      bounds.push(p[0], p[1]);
    });
    d.points.forEach(function (p) {
      L.marker([p[0], p[1]], { icon: icon(MARK[p[2]], 14) }).addTo(map)
        .bindTooltip(p[3], { direction: "top", offset: [0, -6] });
      bounds.push([p[0], p[1]]);
    });
    if (bounds.length) map.fitBounds(L.latLngBounds(bounds).pad(0.08), { maxZoom: 12 });
    current = map;
  }

  window.stormMap = draw;
  draw(document.getElementById("storm-map"));
})();
