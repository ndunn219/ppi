// PE Prep: small progressive enhancements. Every page works without them,
// except the timers, which only display what the server enforces.
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    menu();
    questionTimer();
    sessionCountdown();
    hints();
    estimateGate();
    flashcards();
    localPdf();
    confirms();
    copyButtons();
    printButtons();
  });

  // Phone layout: the sidebar collapses into a menu.
  function menu() {
    var toggle = document.querySelector("[data-menu-toggle]");
    var sidebar = document.querySelector("[data-sidebar]");
    if (!toggle || !sidebar) return;
    toggle.addEventListener("click", function () {
      var open = sidebar.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Seconds spent on this question, sent with the answer. Time with the
  // tab hidden doesn't count, so a coffee break isn't charged to pace.
  function questionTimer() {
    var form = document.querySelector("[data-question]");
    if (!form) return;
    var field = form.querySelector("[data-seconds]");
    var spent = 0;
    var last = Date.now();
    function tick() {
      var now = Date.now();
      if (!document.hidden) spent += (now - last) / 1000;
      last = now;
      field.value = Math.round(spent);
    }
    setInterval(tick, 1000);
    document.addEventListener("visibilitychange", function () { last = Date.now(); });
    form.addEventListener("submit", tick);
  }

  // The session's own clock. The server finishes the session at the
  // deadline whatever this shows.
  function sessionCountdown() {
    var el = document.querySelector("[data-deadline]");
    if (!el) return;
    var deadline = new Date(el.getAttribute("data-deadline")).getTime();
    function pad(n) { return n < 10 ? "0" + n : "" + n; }
    function render() {
      var left = Math.max(0, Math.round((deadline - Date.now()) / 1000));
      var h = Math.floor(left / 3600), m = Math.floor((left % 3600) / 60), s = left % 60;
      el.textContent = (h ? h + ":" + pad(m) : m) + ":" + pad(s);
      el.classList.toggle("low", left < 300);
      if (left === 0) {
        clearInterval(timer);
        window.location.reload();
      }
    }
    var timer = setInterval(render, 1000);
    render();
  }

  function hints() {
    var btn = document.querySelector("[data-hint]");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var text = document.querySelector("[data-hint-text]");
      var used = document.querySelector("[data-hint-used]");
      if (text) text.hidden = false;
      if (used) used.value = "1";
      btn.disabled = true;
      btn.textContent = "Hint shown: half credit";
    });
  }

  // Estimate first: the choices appear only after a range is picked.
  function estimateGate() {
    var gate = document.querySelector("[data-estimate]");
    var after = document.querySelector("[data-after-estimate]");
    if (!gate || !after) return;
    gate.addEventListener("change", function () { after.hidden = false; });
  }

  function flashcards() {
    var card = document.querySelector("[data-flashcard]");
    if (!card) return;
    var grades = document.querySelector("[data-grades]");
    function flip() {
      card.classList.add("is-flipped");
      if (grades) grades.hidden = false;
    }
    card.querySelector("[data-flip]").addEventListener("click", flip);
    document.addEventListener("keydown", function (e) {
      if (e.target.matches("input, textarea, select")) return;
      if (e.key === " " && !card.classList.contains("is-flipped")) { e.preventDefault(); flip(); return; }
      if (!grades || grades.hidden) return;
      var map = { "1": "again", "2": "hard", "3": "good", "4": "easy" };
      if (map[e.key]) grades.querySelector('[value="' + map[e.key] + '"]').click();
    });
  }

  // The student's own PDF opens in the reference panel from their disk.
  // It is turned into a local object URL and never leaves the browser.
  function localPdf() {
    document.querySelectorAll("[data-local-pdf]").forEach(function (input) {
      var panel = input.closest("[data-refpanel]");
      var frame = panel.querySelector("[data-pdf-frame]");
      var empty = panel.querySelector("[data-pdf-empty]");
      var current = null;
      input.addEventListener("change", function () {
        var file = input.files && input.files[0];
        if (!file) return;
        if (current) URL.revokeObjectURL(current);
        current = URL.createObjectURL(file);
        frame.src = current;
        frame.hidden = false;
        if (empty) empty.hidden = true;
      });
    });
  }

  function confirms() {
    document.querySelectorAll("[data-confirm]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        if (!window.confirm(el.getAttribute("data-confirm"))) e.preventDefault();
      });
    });
  }

  function copyButtons() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var text = btn.getAttribute("data-copy");
        var done = function () { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy link"; }, 1500); };
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () { window.prompt("Copy this link", text); });
        else window.prompt("Copy this link", text);
      });
    });
  }

  function printButtons() {
    document.querySelectorAll("[data-print]").forEach(function (btn) {
      btn.addEventListener("click", function () { window.print(); });
    });
  }
})();
