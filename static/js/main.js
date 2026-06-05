document.addEventListener("DOMContentLoaded", function () {
  var navbar = document.getElementById("navbar");
  var hamburger = document.getElementById("navHamburger");
  var drawer = document.getElementById("mobileDrawer");
  var overlay = document.getElementById("drawerOverlay");
  var closeBtn = document.getElementById("drawerClose");
  var themeToggle = document.getElementById("themeToggle");
  var drawerTheme = document.getElementById("drawerThemeToggle");
  var mobileSearchBtn = document.getElementById("mobileSearchBtn");
  var mobileSearchOverlay = document.getElementById("mobileSearchOverlay");
  var mobileSearchClose = document.getElementById("mobileSearchClose");

  function setTheme(isDark) {
    if (isDark) {
      document.body.classList.add("dark-mode");
      document.cookie = "dark_mode=true; path=/; max-age=" + 60 * 60 * 24 * 365;
    } else {
      document.body.classList.remove("dark-mode");
      document.cookie = "dark_mode=false; path=/; max-age=" + 60 * 60 * 24 * 365;
    }
  }

  function toggleTheme() {
    setTheme(!document.body.classList.contains("dark-mode"));
  }

  function openDrawer() {
    drawer.classList.add("open");
    overlay.classList.add("active");
    document.body.style.overflow = "hidden";
    if (hamburger) hamburger.setAttribute("aria-label", "Close navigation menu");
  }

  function closeDrawer() {
    drawer.classList.remove("open");
    overlay.classList.remove("active");
    document.body.style.overflow = "";
    if (hamburger) hamburger.setAttribute("aria-label", "Open navigation menu");
  }

  function toggleDrawer() {
    if (drawer.classList.contains("open")) { closeDrawer(); }
    else { openDrawer(); }
  }

  if (hamburger) { hamburger.addEventListener("click", toggleDrawer); }
  if (closeBtn) { closeBtn.addEventListener("click", closeDrawer); }
  if (overlay) { overlay.addEventListener("click", closeDrawer); }

  if (themeToggle) { themeToggle.addEventListener("click", toggleTheme); }
  if (drawerTheme) { drawerTheme.addEventListener("click", toggleTheme); }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (drawer && drawer.classList.contains("open")) closeDrawer();
      if (mobileSearchOverlay && mobileSearchOverlay.classList.contains("active")) {
        mobileSearchOverlay.classList.remove("active");
      }
    }
  });

  document.querySelectorAll(".drawer-link").forEach(function (link) {
    link.addEventListener("click", closeDrawer);
  });

  if (mobileSearchBtn) {
    mobileSearchBtn.addEventListener("click", function () {
      mobileSearchOverlay.classList.add("active");
      var input = mobileSearchOverlay.querySelector(".mobile-search-input");
      if (input) setTimeout(function () { input.focus(); }, 200);
    });
  }

  if (mobileSearchClose) {
    mobileSearchClose.addEventListener("click", function () {
      mobileSearchOverlay.classList.remove("active");
    });
  }

  var scrollTimeout;
  window.addEventListener("scroll", function () {
    if (scrollTimeout) clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(function () {
      if (window.scrollY > 10) { navbar.classList.add("scrolled"); }
      else { navbar.classList.remove("scrolled"); }
    }, 10);
  });

  var heroInput = document.getElementById("heroSearchInput");
  if (heroInput) {
    heroInput.addEventListener("input", function () {
      var q = this.value.trim();
      var list = document.getElementById("heroSuggestions");
      if (q.length < 2) { if (list) { list.classList.remove("active"); list.innerHTML = ""; } return; }
      fetch("/search/suggest/?q=" + encodeURIComponent(q))
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!list) return;
          list.innerHTML = "";
          if (data.length === 0) { list.classList.remove("active"); return; }
          data.forEach(function (item) {
            var div = document.createElement("div");
            div.className = "suggestion-item";
            div.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg><span>' + item.label + "</span>";
            div.addEventListener("click", function () { window.location.href = item.url; });
            list.appendChild(div);
          });
          list.classList.add("active");
        })
        .catch(function () {});
    });
    document.addEventListener("click", function (e) {
      var wrapper = document.querySelector(".hero-search-wrapper");
      if (wrapper && !wrapper.contains(e.target)) {
        var list = document.getElementById("heroSuggestions");
        if (list) list.classList.remove("active");
      }
    });
  }
});
