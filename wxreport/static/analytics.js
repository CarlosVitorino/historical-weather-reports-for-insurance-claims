/* Analytics (Umami, cookieless, self-hosted). Loads before the tracker, so weScrub exists when it starts.

   weScrub runs on every payload before it leaves: only query keys that describe what was asked of a public page are
   kept (filters, a storm day, campaign tags). /order can be opened prefilled with an address and an email; those never
   leave the browser. An outside referrer keeps only its site.

   Events are fixed words, never anything a visitor typed:
     order_cta      a link to the order page        where: header | menu | hero | storm_card | storm_page | guide | page
     order_submit   the address form is sent         (pressed, not succeeded)
     sample_report  the sample PDF is opened         where: nav | menu | page
     storm_day      another storm day on a city page via: chip | list | pager | latest   (storm-city.js)
     storm_filter   the Storm Reports filters        (storm-filters.js)

   A browser the owner switched off in /admin (localStorage umami.disabled) sends nothing: the tracker checks it. */
(function () {
  "use strict";
  var KEEP = /^(q|state|period|kind|sort|page|day|loss_date|utm_[a-z]+)$/;

  window.weScrub = function (_type, payload) {
    try {
      var url = new URL(payload.url, location.origin);
      var kept = new URLSearchParams();
      url.searchParams.forEach(function (v, k) { if (KEEP.test(k)) kept.append(k, v); });
      url.search = kept.toString();
      payload.url = url.origin + url.pathname + url.search;
    } catch (e) {
      return false;
    }
    if (payload.referrer && !payload.referrer.startsWith("/")) {
      try { payload.referrer = new URL(payload.referrer).origin; } catch (e) { payload.referrer = ""; }
    } else if (payload.referrer) {
      payload.referrer = payload.referrer.split(/[?#]/)[0];
    }
    return payload;
  };

  window.weTrack = function (name, data) {
    if (window.umami && typeof window.umami.track === "function") window.umami.track(name, data);
  };

  function where(el) {
    if (el.closest(".mnav-panel")) return "menu";
    if (el.closest("header.top")) return "header";
    if (el.closest(".hero")) return "hero";
    if (el.closest(".sr-panel")) return "storm_card";
    if (el.closest(".sr-wrap")) return "storm_page";
    if (el.closest(".article")) return "guide";
    return "page";
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var path = a.pathname || "";
    if (path === "/order") weTrack("order_cta", { where: where(a) });
    else if (/sample-report\.pdf$/.test(path)) weTrack("sample_report", { where: where(a) === "header" ? "nav" : where(a) === "menu" ? "menu" : "page" });
  }, true);

  document.addEventListener("submit", function (e) {
    if (e.target && e.target.id === "order-form") weTrack("order_submit");
  }, true);
})();
