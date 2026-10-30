/* City page: picking a storm day swaps the storm card in place (no reload, no jump) and keeps a real URL, so the
   day can be shared and Back works. On phones the days are a strip of chips on the card, and "All days" opens the
   full list as a bottom sheet. Without JavaScript the same links load the page at the card (#storm). */
(function () {
  "use strict";
  if (!window.fetch || !window.history || !window.DOMParser) return;
  document.documentElement.classList.add("sr-js");
  var busy = false, backdrop = document.createElement("div");
  backdrop.className = "sr-backdrop";

  function list() { return document.getElementById("storm-days"); }

  function openSheet() {
    document.body.classList.add("sr-sheet-open");
    document.body.appendChild(backdrop);
    var close = list().querySelector("[data-sheet-close]");
    close.hidden = false;
    close.focus();
    centreCurrent();
  }
  function closeSheet() {
    document.body.classList.remove("sr-sheet-open");
    backdrop.remove();
  }

  // Show the picked day in the strip and in the list, scrolling only their own boxes, never the page.
  function centreCurrent() {
    var strip = document.querySelector(".sr-chips-x"), chip = strip && strip.querySelector("[aria-current]");
    if (chip) strip.scrollLeft = chip.offsetLeft - (strip.clientWidth - chip.offsetWidth) / 2;
    var box = list().querySelector(".sr-dscroll"), cur = box.querySelector("[aria-current]");
    if (cur && box.scrollHeight > box.clientHeight) box.scrollTop = cur.offsetTop - box.clientHeight / 3;
  }

  function swap(url, push) {
    if (busy) return;
    busy = true;
    var panel = document.getElementById("storm");
    panel.setAttribute("aria-busy", "true");
    fetch(url, { headers: { Accept: "text/html" } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var next = doc.getElementById("storm"), days = doc.getElementById("storm-days");
        if (!next || !days) throw new Error("no storm card");
        closeSheet();
        panel.replaceWith(next);
        list().replaceWith(days);
        if (push) history.pushState({}, "", url.split("#")[0]);
        if (window.stormMap) window.stormMap(document.getElementById("storm-map"));
        var top = next.getBoundingClientRect().top;
        if (top < 0 || top > window.innerHeight * 0.6) next.scrollIntoView({ behavior: "smooth", block: "start" });
        next.focus({ preventScroll: true });
        centreCurrent();
      })
      .catch(function () { location.href = url; })
      .then(function () { busy = false; });
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target : null;
    if (!t) return;
    if (t.closest("[data-sheet]")) { e.preventDefault(); openSheet(); return; }
    if (t.closest("[data-sheet-close]")) { closeSheet(); return; }
    var a = t.closest("a[data-day]");
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    swap(a.href, true);
    if (window.weTrack) {
      var via = a.closest(".sr-chips-x") ? "chip" : a.closest("#storm-days") ? "list" : a.closest(".sr-pager") ? "pager"
        : "latest";
      window.weTrack("storm_day", { via: via });
    }
  });
  backdrop.addEventListener("click", closeSheet);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeSheet(); });
  window.addEventListener("popstate", function () { swap(location.href, false); });
  centreCurrent();
})();
