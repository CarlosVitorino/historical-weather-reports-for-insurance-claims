/* Order form: address field and map pin, kept in sync both ways. The form still works without this script.

   Address → pin: picking a suggestion, or pausing / pressing Enter / leaving the field after typing a full
   address, looks it up (US Census first) and moves the pin.
   Pin → address: clicking the map or dragging the pin fills the address field with the nearest address
   (or "Map pin in <county>, <state>" when no street address is known).
   The hidden lat/lon fields always hold the pin, which is what the report is built for. */
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
  function getJSON(url) { return fetch(url).then(function (r) { return r.json(); }); }

  /* ---------- confirm page: show where the report will be centred ---------- */
  var cm = document.getElementById("confirm-map");
  if (cm && window.L) {
    var c = [parseFloat(cm.dataset.lat), parseFloat(cm.dataset.lon)];
    var cls = layers();
    var m0 = L.map(cm, { scrollWheelZoom: false, layers: [cls.Map] }).setView(c, 17);
    viewToggle(m0, cls);
    L.marker(c, { icon: pinIcon(), interactive: false }).addTo(m0);
  }

  /* ---------- order form ---------- */
  var form = document.getElementById("order-form");
  if (!form || !window.L) return;               // no map library: keep the plain fields
  var input = document.getElementById("address");
  var list = document.getElementById("ac-list");
  var hint = document.getElementById("addr-hint");
  var lat = document.getElementById("lat"), lon = document.getElementById("lon");
  var wrap = document.getElementById("map-wrap");
  var note = document.getElementById("map-note");
  var pinned = document.getElementById("pinned");
  var map, marker, items = [], active = -1, suggestTimer = null, geoTimer = null, seq = 0, geoSeq = 0;
  var synced = false;                            // does the pin match the text in the address field?

  document.getElementById("coords").hidden = true;   // the map replaces the raw latitude/longitude fields
  wrap.hidden = false;

  var ls = layers();
  map = L.map("map", { layers: [ls.Map], scrollWheelZoom: false }).setView(US, 4);
  viewToggle(map, ls);
  map.on("click", function (e) { movePin(e.latlng, true); });

  function say(el, text, kind) { el.textContent = text || ""; el.className = "fine" + (kind ? " " + kind : ""); }

  /* pin → hidden fields (and optionally → address text) */
  function movePin(ll, fromMap, zoom) {
    if (!marker) {
      marker = L.marker(ll, { draggable: true, icon: pinIcon(), autoPan: true }).addTo(map);
      marker.on("dragend", function () { movePin(marker.getLatLng(), true); });
    } else {
      marker.setLatLng(ll);
    }
    if (zoom) map.setView(ll, zoom); else if (!map.getBounds().contains(ll)) map.panTo(ll);
    lat.value = ll.lat.toFixed(6); lon.value = ll.lng.toFixed(6);
    pinned.classList.add("on");
    if (fromMap) fillFromPin(ll);
  }
  function fillFromPin(ll) {
    var mine = ++geoSeq;
    say(note, "Finding the address at the pin…");
    getJSON("/api/reverse?lat=" + ll.lat.toFixed(6) + "&lon=" + ll.lng.toFixed(6)).then(function (d) {
      if (mine !== geoSeq) return;
      input.value = d.label;
      synced = true; say(hint, "");
      if (d.ok && !d.in_us) say(note, "That point isn't inside a US county. Reports cover US locations only.", "warn");
      else say(note, "Pin " + (d.county ? "in " + d.county + ", " + d.state : "placed") +
                     ". Drag it onto the exact building if needed.");
    }).catch(function () {
      if (mine !== geoSeq) return;
      input.value = "Map pin at " + ll.lat.toFixed(5) + ", " + ll.lng.toFixed(5);
      synced = true; say(note, "Pin placed. Drag it onto the exact building if needed.");
    });
  }

  /* address text → pin */
  function locateText(thenSubmit) {
    var q = input.value.trim();
    if (q.length < 6) return Promise.resolve(false);
    var mine = ++geoSeq;
    say(hint, "Looking up the address…");
    return getJSON("/api/geocode?q=" + encodeURIComponent(q)).then(function (d) {
      if (mine !== geoSeq) return false;
      if (!d.ok) {
        say(hint, "No match yet. Include the city and state (e.g. 5299 DTC Blvd, Greenwood Village, CO), " +
                  "pick a suggestion, or click the map.", "warn");
        return false;
      }
      synced = true;
      say(hint, "Found: " + d.label, "ok");
      movePin(L.latLng(d.lat, d.lon), false, 18);
      say(note, "Check the pin is on the property. Drag it onto the exact building if needed.");
      return true;
    }).catch(function () { if (mine === geoSeq) say(hint, "Address lookup is unavailable. Click the map instead.", "warn"); return false; });
  }

  /* suggestions */
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
    ++geoSeq;
    input.value = it.label;
    close();
    synced = true;
    say(hint, "");
    movePin(L.latLng(it.lat, it.lon), false, it.exact ? 18 : 16);
    say(note, it.exact ? "Check the pin is on the property. Drag it onto the exact building if needed."
                       : "Drag the pin onto the property, or click the map to move it.");
  }

  input.addEventListener("input", function () {
    synced = false;
    clearTimeout(suggestTimer); clearTimeout(geoTimer);
    var q = input.value.trim();
    if (q.length < 3) { items = []; close(); say(hint, ""); return; }
    suggestTimer = setTimeout(function () {
      var mine = ++seq;
      getJSON("/api/suggest?q=" + encodeURIComponent(q)).then(function (d) {
        if (mine !== seq) return;
        items = d.results || []; render(); highlight(-1);
        if (d.ok === false) say(hint, "Suggestions are unavailable right now. Type the full address with city " +
                                      "and state, or click the map.", "warn");
      }).catch(function () { items = []; close(); });
    }, 200);
    // Once typing pauses on something address-like, move the pin to it.
    if (/\d/.test(q) && q.length >= 10) geoTimer = setTimeout(function () { if (!synced) locateText(); }, 1100);
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown" && items.length) { e.preventDefault(); highlight(Math.min(active + 1, items.length - 1)); }
    else if (e.key === "ArrowUp" && items.length) { e.preventDefault(); highlight(Math.max(active - 1, 0)); }
    else if (e.key === "Escape") { close(); }
    else if (e.key === "Enter") {
      e.preventDefault();
      if (!list.hidden && active >= 0) choose(active);
      else { close(); clearTimeout(geoTimer); locateText(); }
    }
  });
  input.addEventListener("blur", function () {
    setTimeout(close, 120);
    clearTimeout(geoTimer);
    if (!synced && input.value.trim().length >= 6) setTimeout(function () { if (!synced) locateText(); }, 150);
  });

  /* On submit the pin must match the address: resolve the text first if it changed since the last pin. */
  form.addEventListener("submit", function (e) {
    if (synced && lat.value) return;
    e.preventDefault();
    if (!input.value.trim()) {
      say(hint, "Enter the property address, or click the map to place a pin.", "warn");
      input.focus();
      return;
    }
    locateText().then(function (ok) { if (ok) form.submit(); else input.focus(); });
  });

  if (lat.value && lon.value) {                  // returning with an error: restore the pin
    movePin(L.latLng(parseFloat(lat.value), parseFloat(lon.value)), false, 17);
    synced = true;
  }

  /* "Order" / "Start your report" buttons focus the address field */
  Array.prototype.forEach.call(document.querySelectorAll('a[href$="#order"]'), function (a) {
    a.addEventListener("click", function () { setTimeout(function () { input.focus({ preventScroll: true }); }, 400); });
  });
  setTimeout(function () { map.invalidateSize(); }, 100);
})();
