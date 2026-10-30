/* Storm Reports table filters.
   Desktop: the filters sit in one row and apply as soon as one changes.
   Phones: a search field and a filter button; the button opens the other filters as a bottom sheet with Apply.
   Without JavaScript every filter is visible and the Apply button submits the form. */
(function () {
  "use strict";
  var form = document.querySelector("form[data-autosubmit]");
  if (!form) return;
  var button = form.querySelector(".sr-fbtn"), sheet = form.querySelector(".sr-fsheet");
  var backdrop = document.createElement("div");
  backdrop.className = "sr-backdrop";
  form.classList.add("js");
  button.hidden = false;

  function phone() { return getComputedStyle(button).display !== "none"; }
  function submit() { form.requestSubmit ? form.requestSubmit() : form.submit(); }

  function open() {
    form.classList.add("open");
    document.body.appendChild(backdrop);
    button.setAttribute("aria-expanded", "true");
    var first = sheet.querySelector("select");
    if (first) first.focus();
  }
  function close() {
    form.classList.remove("open");
    backdrop.remove();
    button.setAttribute("aria-expanded", "false");
    button.focus();
  }

  button.addEventListener("click", open);
  form.querySelector(".sr-fclose").addEventListener("click", close);
  backdrop.addEventListener("click", close);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && form.classList.contains("open")) close(); });

  // Leave empty and default values out of the URL: /storm-reports?period=all, not ?q=&state=&period=all&kind=all…
  var DEFAULTS = { q: "", state: "", period: "30d", kind: "all", sort: "date" };
  form.addEventListener("submit", function () {
    if (window.weTrack) {
      window.weTrack("storm_filter", { period: form.period.value, kind: form.kind.value, sort: form.sort.value,
                                       state: form.state.value ? "one" : "all", city: form.q.value.trim() ? "yes" : "no" });
    }
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.name in DEFAULTS && el.value.trim() === DEFAULTS[el.name]) el.disabled = true;
    });
    setTimeout(function () { Array.prototype.forEach.call(form.elements, function (el) { el.disabled = false; }); });
  });

  form.addEventListener("change", function (e) {
    if (e.target.tagName === "SELECT" && !phone()) submit();   // on phones the sheet's Apply button submits
  });

  // Picking a suggestion from the city list applies it at once; typing waits for Enter.
  var q = form.querySelector("input[name=q]");
  var list = document.getElementById(q.getAttribute("list"));
  q.addEventListener("input", function () {
    for (var i = 0; i < list.options.length; i++) {
      if (list.options[i].value === q.value) { submit(); return; }
    }
  });
})();
