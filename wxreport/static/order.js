/* Order form: address autocomplete and map pin. The form still works without this script. */
(function () {
  "use strict";
  var US = [39.8, -98.6];

  function layers() {
    var street = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
    });
    var sat = L.tileLayer(
      "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 19, maxNativeZoom: 16, attribution: "Imagery: USGS The National Map" });
    return { Map: street, Satellite: sat };
  }

  /* Map | Satellite toggle (a plain two-button control, styled by the page). */
  function viewToggle(map, ls) {
    var Ctl = L.Control.extend({
      options: { position: "topright" },
      onAdd: function () {
        var box = L.DomUtil.create("div", "mapview");
        box.setAttribute("role", "group"); box.setAttribute("aria-label", "Map view");
        Object.keys(ls).forEach(function (name) {
          var b = L.DomUtil.create("button", "", box);
          b.type = "button"; b.textContent = name;
          b.setAttribute("aria-pressed", map.hasLayer(ls[name]) ? "true" : "false");
          L.DomEvent.on(b, "click", function (e) {
            L.DomEvent.stop(e);
            Object.keys(ls).forEach(function (n) { map.removeLayer(ls[n]); });
            map.addLayer(ls[name]);
            Array.prototype.forEach.call(box.children, function (x) {
              x.setAttribute("aria-pressed", x === b ? "true" : "false");
            });
          });
        });
        L.DomEvent.disableClickPropagation(box);
        return box;
      }
    });
    new Ctl().addTo(map);
  }

  function pinIcon() {
    return L.divIcon({ className: "", html: '<div class="pin"></div>', iconSize: [22, 22], iconAnchor: [11, 26] });
  }

  /* ---------- confirm page: show where the report will be centred ---------- */
  var cm = document.getElementById("confirm-map");
  if (cm && window.L) {
    var c = [parseFloat(cm.dataset.lat), parseFloat(cm.dataset.lon)];
    var ls = layers();
    var m0 = L.map(cm, { scrollWheelZoom: false, layers: [ls.Map] }).setView(c, 17);
    viewToggle(m0, ls);
    L.marker(c, { icon: pinIcon(), interactive: false }).addTo(m0);
  }

  /* ---------- order form ---------- */
  var form = document.getElementById("order-form");
  if (!form) return;
  var input = document.getElementById("address");
  var list = document.getElementById("ac-list");
  var lat = document.getElementById("lat"), lon = document.getElementById("lon");
  var coords = document.getElementById("coords");
  var toggle = document.getElementById("pin-toggle");
  var wrap = document.getElementById("map-wrap");
  var note = document.getElementById("map-note");
  var pinned = document.getElementById("pinned");
  var map = null, marker = null, source = null, items = [], active = -1, timer = null, seq = 0;

  if (!window.L) return;                         // no map library: keep the plain fields
  toggle.hidden = false;
  var hadCoords = lat.value && lon.value;
  coords.hidden = true;                          // the map replaces the raw latitude/longitude fields

  function setCoords(ll) {
    lat.value = ll.lat.toFixed(6); lon.value = ll.lng.toFixed(6);
    pinned.classList.add("on");
  }
  function clearCoords() {
    lat.value = ""; lon.value = ""; pinned.classList.remove("on");
  }
  function describe(ll) {
    note.textContent = "Checking the location…";
    fetch("/api/where?lat=" + ll.lat.toFixed(6) + "&lon=" + ll.lng.toFixed(6))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) note.textContent = "Pin placed. Drag it onto the exact building if needed.";
        else if (!d.in_us) note.textContent = "That point isn't inside a US county. Reports cover US locations only.";
        else note.textContent = "Pin in " + d.county + ", " + d.state + ". Drag it onto the exact building if needed.";
      })
      .catch(function () { note.textContent = "Pin placed. Drag it onto the exact building if needed."; });
  }
  function ensureMap(center, zoom) {
    wrap.hidden = false;
    if (!map) {
      var ls = layers();
      map = L.map("map", { layers: [ls.Map] }).setView(center, zoom);
      viewToggle(map, ls);
      map.on("click", function (e) { place(e.latlng, "pin"); });
    } else {
      map.setView(center, zoom);
    }
    setTimeout(function () { map.invalidateSize(); }, 50);
  }
  function place(ll, why) {
    source = why;
    if (!marker) {
      marker = L.marker(ll, { draggable: true, icon: pinIcon(), autoPan: true }).addTo(map);
      marker.on("dragend", function () { source = "pin"; setCoords(marker.getLatLng()); describe(marker.getLatLng()); });
    } else {
      marker.setLatLng(ll);
    }
    setCoords(ll);
    if (why === "pin") describe(ll);
  }

  toggle.addEventListener("click", function () {
    if (!wrap.hidden && map) { map.invalidateSize(); return; }
    if (lat.value && lon.value) {
      var ll = L.latLng(parseFloat(lat.value), parseFloat(lon.value));
      ensureMap(ll, 17); place(ll, "pin");
    } else {
      ensureMap(US, 4);
      note.textContent = "Zoom in and click the property to place the pin.";
    }
  });
  if (hadCoords) toggle.click();

  /* autocomplete */
  function close() { list.hidden = true; input.setAttribute("aria-expanded", "false"); active = -1; }
  function render() {
    list.innerHTML = "";
    items.forEach(function (it, i) {
      var li = document.createElement("li");
      li.id = "ac-" + i; li.setAttribute("role", "option");
      li.textContent = it.label;
      if (!it.exact) {
        var sm = document.createElement("small"); sm.textContent = "Street or area: place the pin on the building";
        li.appendChild(sm);
      }
      li.addEventListener("mousedown", function (e) { e.preventDefault(); choose(i); });
      list.appendChild(li);
    });
    var attr = document.createElement("li");
    attr.className = "attr"; attr.textContent = "Suggestions: © OpenStreetMap contributors";
    list.appendChild(attr);
    list.hidden = items.length === 0;
    input.setAttribute("aria-expanded", items.length ? "true" : "false");
  }
  function highlight(i) {
    active = i;
    Array.prototype.forEach.call(list.querySelectorAll("[role=option]"), function (li, j) {
      li.setAttribute("aria-selected", j === i ? "true" : "false");
    });
    input.setAttribute("aria-activedescendant", i >= 0 ? "ac-" + i : "");
  }
  function choose(i) {
    var it = items[i];
    input.value = it.label;
    close();
    var ll = L.latLng(it.lat, it.lon);
    ensureMap(ll, it.exact ? 18 : 16);
    place(ll, "suggest");
    note.textContent = it.exact ? "Check the pin is on the property. Drag it onto the exact building if needed."
                                : "Drag the pin onto the property, or click the map to move it.";
  }
  input.addEventListener("input", function () {
    if (source === "suggest") { clearCoords(); source = null; }
    clearTimeout(timer);
    var q = input.value.trim();
    if (q.length < 3) { items = []; close(); return; }
    timer = setTimeout(function () {
      var mine = ++seq;
      fetch("/api/suggest?q=" + encodeURIComponent(q))
        .then(function (r) { return r.json(); })
        .then(function (d) { if (mine === seq) { items = d.results || []; render(); highlight(-1); } })
        .catch(function () { items = []; close(); });
    }, 220);
  });
  input.addEventListener("keydown", function (e) {
    if (list.hidden || !items.length) return;
    if (e.key === "ArrowDown") { e.preventDefault(); highlight(Math.min(active + 1, items.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); highlight(Math.max(active - 1, 0)); }
    else if (e.key === "Enter" && active >= 0) { e.preventDefault(); choose(active); }
    else if (e.key === "Escape") { close(); }
  });
  input.addEventListener("blur", function () { setTimeout(close, 120); });

  form.addEventListener("submit", function (e) {
    if (!input.value.trim() && !(lat.value && lon.value)) {
      e.preventDefault();
      input.focus();
      input.setCustomValidity("Enter the property address, or place a pin on the map.");
      input.reportValidity();
      setTimeout(function () { input.setCustomValidity(""); }, 2000);
    }
  });

  /* "Start your report" / "Order" buttons focus the address field */
  Array.prototype.forEach.call(document.querySelectorAll('a[href$="#order"]'), function (a) {
    a.addEventListener("click", function () { setTimeout(function () { input.focus({ preventScroll: true }); }, 400); });
  });
})();
