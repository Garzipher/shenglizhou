/* Progressive navigation for this small static site. Ordinary links still work. */
(function () {
  "use strict";
  if (!/^https?:$/.test(location.protocol) || !window.fetch || !window.DOMParser || !window.AbortController) return;
  var root = new URL("../../", document.currentScript.src);
  var files = ["index.html", "skills.html", "projects.html", "career.html", "resume.html"];
  var paths = new Set();
  ["", "en/"].forEach(function (lang) {
    files.forEach(function (file) { paths.add(new URL(lang + file, root).pathname); });
  });
  paths.add(root.pathname);
  paths.add(new URL("en/", root).pathname);
  var cache = new Map();
  var sequence = 0;
  var entrySequence = 0;
  var scrollPositions = new Map();
  var restoring = false;
  var connection = navigator.connection;
  var allowPrefetch = !connection || (!connection.saveData && !/2g/.test(connection.effectiveType));
  function key(url) {
    var path = url.pathname;
    return path.endsWith("/") ? path + "index.html" : path;
  }
  function eligible(url) {
    return url.origin === root.origin && paths.has(url.pathname) && !url.search && !url.hash;
  }
  function load(url) {
    var id = key(url);
    if (!cache.has(id)) {
      var controller = new AbortController();
      var timeout = setTimeout(function () { controller.abort(); }, 8000);
      var task = fetch(url.href, {signal: controller.signal, credentials: "same-origin"})
        .then(function (response) {
          if (!response.ok || !/text\/html/i.test(response.headers.get("content-type") || "")) throw new Error("HTML unavailable");
          return response.text();
        }).then(function (source) {
          var doc = new DOMParser().parseFromString(source, "text/html");
          if (!doc.querySelector("#main .page-content") || !doc.querySelector(".masthead")) throw new Error("Invalid page");
          return doc;
        }).catch(function (error) { cache.delete(id); throw error; })
        .finally(function () { clearTimeout(timeout); });
      cache.set(id, task);
    }
    return cache.get(id);
  }
  function rememberScroll() {
    var state = Object.assign({}, history.state, {resumeSite: true, x: scrollX, y: scrollY});
    if (!state.resumeEntry) state.resumeEntry = Date.now() + "_" + (++entrySequence);
    scrollPositions.set(state.resumeEntry, {x: scrollX, y: scrollY});
    history.replaceState(state, "", location.href);
  }
  async function visit(url, fromHistory, position) {
    var ticket = ++sequence;
    var oldMain = document.getElementById("main");
    oldMain.setAttribute("aria-busy", "true");
    try {
      var doc = await load(url);
      if (ticket !== sequence) return;
      var main = document.importNode(doc.getElementById("main"), true);
      var masthead = document.importNode(doc.querySelector(".masthead"), true);
      // Resolve every relative URL against the destination, including language changes.
      [main, masthead].forEach(function (section) {
        section.querySelectorAll("[href], [src]").forEach(function (el) {
          ["href", "src"].forEach(function (attr) {
            if (el.hasAttribute(attr)) el.setAttribute(attr, new URL(el.getAttribute(attr), url).href);
          });
        });
      });
      if (!fromHistory) {
        rememberScroll();
        history.pushState({resumeSite: true, resumeEntry: Date.now() + "_" + (++entrySequence), x: 0, y: 0}, "", url.href);
      }
      document.documentElement.lang = doc.documentElement.lang;
      document.title = doc.title;
      var description = document.querySelector('meta[name="description"]');
      if (description) description.content = doc.querySelector('meta[name="description"]').content;
      document.querySelectorAll('link[rel="alternate"]').forEach(function (link) { link.remove(); });
      doc.querySelectorAll('link[rel="alternate"]').forEach(function (link) {
        var alternate = document.importNode(link, true);
        alternate.href = new URL(link.getAttribute("href"), url).href;
        document.head.appendChild(alternate);
      });
      document.querySelector(".masthead").replaceWith(masthead);
      oldMain.replaceWith(main);
      window.updateNav();
      restoring = true;
      if (!fromHistory) {
        var article = main.querySelector("article");
        article.setAttribute("tabindex", "-1");
        article.style.outline = "none";
        article.focus({preventScroll: true});
      }
      window.scrollTo(position ? position.x : 0, position ? position.y : 0);
      requestAnimationFrame(function () { restoring = false; });
    } catch (error) {
      if (ticket === sequence) {
        if (fromHistory) location.replace(url.href);
        else location.assign(url.href);
      }
    } finally {
      if (ticket === sequence) document.getElementById("main").removeAttribute("aria-busy");
    }
  }
  cache.set(key(new URL(location.href)), Promise.resolve(document.cloneNode(true)));
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  rememberScroll();
  document.addEventListener("click", function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var a = event.target.closest("a[href]");
    if (!a || a.hasAttribute("download") || (a.target && a.target !== "_self")) return;
    var url = new URL(a.href);
    if (!eligible(url)) return;
    event.preventDefault();
    if (key(url) === key(new URL(location.href))) {
      sequence++;
      document.getElementById("main").removeAttribute("aria-busy");
      window.updateNav();
      return;
    }
    visit(url, false);
  });
  ["pointerover", "focusin", "touchstart"].forEach(function (type) {
    document.addEventListener(type, function (event) {
      if (!allowPrefetch) return;
      var a = event.target.closest("a[href]");
      if (!a) return;
      var url = new URL(a.href);
      if (eligible(url)) load(url).catch(function () {});
    }, {passive: true});
  });
  window.addEventListener("scroll", function () {
    if (!restoring && history.state && history.state.resumeEntry) {
      scrollPositions.set(history.state.resumeEntry, {x: scrollX, y: scrollY});
    }
  }, {passive: true});
  window.addEventListener("popstate", function (event) {
    var url = new URL(location.href);
    if (eligible(url)) visit(url, true, scrollPositions.get(event.state && event.state.resumeEntry) || event.state);
    else location.reload();
  });
})();
