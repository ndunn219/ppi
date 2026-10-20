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

  // --- Dialogs ----------------------------------------------------------------
  //
  // Styled replacements for alert(), confirm() and prompt(), built on the
  // native <dialog> element (focus moves in and back, Escape cancels, the
  // page behind is inert). Each returns a Promise:
  //
  //   PEDialog.confirm({title, message, ok, cancel, tone}) -> true / false
  //   PEDialog.alert({title, message, ok})                  -> undefined
  //   PEDialog.prompt({title, message, value, ok, readonly, copy}) -> text / null
  //
  // tone "danger" gives the confirm button a red style.
  var PEDialog = (window.PEDialog = (function () {
    function open(opts) {
      return new Promise(function (resolve) {
        var dlg = document.createElement("dialog");
        dlg.className = "pe-dialog" + (opts.tone ? " is-" + opts.tone : "");
        dlg.setAttribute("aria-labelledby", "pe-dialog-title");
        var field = opts.kind === "prompt"
          ? '<div class="pe-dialog-field"><input type="text" class="pe-dialog-input"' + (opts.readonly ? " readonly" : "") + ' aria-label="' + esc(opts.title || "Value") + '"></div>'
          : "";
        var cancel = opts.kind === "alert" ? "" : '<button type="button" class="btn btn-ghost" data-dialog-cancel>' + esc(opts.cancel || "Cancel") + "</button>";
        var okClass = opts.tone === "danger" ? "btn btn-danger" : "btn btn-primary";
        dlg.innerHTML =
          '<form method="dialog" class="pe-dialog-body">' +
          '<h2 id="pe-dialog-title">' + esc(opts.title || "") + "</h2>" +
          (opts.message ? '<p class="pe-dialog-message">' + esc(opts.message) + "</p>" : "") +
          field +
          '<div class="pe-dialog-actions">' + cancel +
          '<button type="submit" class="' + okClass + '" value="ok" data-dialog-ok>' + esc(opts.ok || "OK") + "</button></div>" +
          "</form>";
        document.body.appendChild(dlg);
        var input = dlg.querySelector(".pe-dialog-input");
        if (input) input.value = opts.value || "";
        var result = opts.kind === "confirm" ? false : null;

        dlg.querySelector("form").addEventListener("submit", function (e) {
          e.preventDefault();
          if (opts.kind === "prompt" && opts.copy && input) {
            input.select();
            var copied = navigator.clipboard ? navigator.clipboard.writeText(input.value) : Promise.reject();
            copied.then(function () { result = input.value; dlg.close(); }, function () {
              try { document.execCommand("copy"); result = input.value; dlg.close(); } catch (err) { input.select(); }
            });
            return;
          }
          result = opts.kind === "confirm" ? true : (input ? input.value : undefined);
          dlg.close();
        });
        var cancelBtn = dlg.querySelector("[data-dialog-cancel]");
        if (cancelBtn) cancelBtn.addEventListener("click", function () { dlg.close(); });
        dlg.addEventListener("click", function (e) { if (e.target === dlg && opts.kind !== "alert") dlg.close(); });
        dlg.addEventListener("close", function () {
          dlg.remove();
          resolve(opts.kind === "alert" ? undefined : result);
        });
        dlg.showModal();
        if (input) { input.focus(); input.select(); }
        else dlg.querySelector(opts.kind === "confirm" && opts.tone === "danger" ? "[data-dialog-cancel]" : "[data-dialog-ok]").focus();
      });
    }

    function esc(t) {
      return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
    }

    return {
      confirm: function (o) { return open(Object.assign({ kind: "confirm", title: "Are you sure?" }, o)); },
      alert: function (o) { return open(Object.assign({ kind: "alert" }, o)); },
      prompt: function (o) { return open(Object.assign({ kind: "prompt" }, o)); },
    };
  })());

  // Buttons and links with data-confirm ask first. Optional attributes:
  // data-confirm-title, data-confirm-ok (button label), data-confirm-tone.
  function confirms() {
    document.querySelectorAll("[data-confirm]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        if (el.dataset.confirmed === "1") { el.dataset.confirmed = ""; return; }
        e.preventDefault();
        PEDialog.confirm({
          title: el.getAttribute("data-confirm-title") || "Are you sure?",
          message: el.getAttribute("data-confirm"),
          ok: el.getAttribute("data-confirm-ok") || "Continue",
          tone: el.getAttribute("data-confirm-tone") || "",
        }).then(function (yes) {
          if (!yes) return;
          if (el.form && el.type === "submit") {
            // Submit with this button, so its name and value are sent.
            if (el.form.requestSubmit) el.form.requestSubmit(el);
            else { el.dataset.confirmed = "1"; el.click(); }
          } else if (el.href) {
            window.location.href = el.href;
          } else {
            el.dataset.confirmed = "1";
            el.click();
          }
        });
      });
    });
  }

  function copyButtons() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var text = btn.getAttribute("data-copy");
        var label = btn.textContent;
        var done = function () { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = label; }, 1500); };
        var fallback = function () {
          PEDialog.prompt({ title: "Copy this link", message: "Your browser blocked copying automatically. Copy the link below.", value: text, readonly: true, copy: true, ok: "Copy", cancel: "Close" })
            .then(function (v) { if (v) done(); });
        };
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, fallback);
        else fallback();
      });
    });
  }

  function printButtons() {
    document.querySelectorAll("[data-print]").forEach(function (btn) {
      btn.addEventListener("click", function () { window.print(); });
    });
  }
})();
