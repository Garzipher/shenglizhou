/* Keep the reference navigation's appearance; recalculate after layout changes. */
(function () {
  "use strict";
  function layout() {
    var nav = document.getElementById("site-nav");
    if (!nav) return;
    var button = nav.querySelector("button");
    var visible = nav.querySelector(".visible-links");
    var hidden = nav.querySelector(".hidden-links");
    while (hidden.firstElementChild) visible.appendChild(hidden.firstElementChild);
    button.classList.add("hidden");
    button.classList.remove("close");
    hidden.classList.add("hidden");
    var available = nav.clientWidth - nav.clientWidth * 0.01;
    if (visible.getBoundingClientRect().width > available) {
      button.classList.remove("hidden");
      available -= button.getBoundingClientRect().width + 30;
      while (visible.getBoundingClientRect().width > available && visible.children.length > 1) {
        hidden.insertBefore(visible.lastElementChild, hidden.firstElementChild);
      }
    }
    button.setAttribute("count", String(hidden.children.length));
    button.setAttribute("aria-expanded", "false");
  }
  window.updateNav = layout;
  window.addEventListener("resize", layout);
  window.addEventListener("load", layout);
  document.addEventListener("click", function (event) {
    var button = event.target.closest("#site-nav button");
    if (!button) return;
    var hidden = button.closest("nav").querySelector(".hidden-links");
    var open = hidden.classList.contains("hidden");
    hidden.classList.toggle("hidden", !open);
    button.classList.toggle("close", open);
    button.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    var button = document.querySelector("#site-nav button.close");
    if (button) { layout(); button.focus(); }
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
  layout();
})();
