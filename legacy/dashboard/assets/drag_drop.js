/**
 * Drag-and-drop bridge: KPI badge → chart drop zone.
 *
 * Flow:
 *   1. User drags a badge with [data-metric] attribute.
 *   2. dragstart stores the metric key in dataTransfer.
 *   3. dragover on .chart-drop-zone allows the drop.
 *   4. drop reads the metric key, sets window._droppedMetric,
 *      then programmatically clicks the hidden #_drop-btn.
 *      A Dash clientside_callback picks up the click, reads the
 *      global, and writes it into drop-metric-store — which
 *      triggers the server-side chart callback.
 */

document.addEventListener("dragstart", function (e) {
  var badge = e.target.closest("[data-metric]");
  if (!badge) return;
  e.dataTransfer.setData("text/plain", badge.getAttribute("data-metric"));
  e.dataTransfer.effectAllowed = "copy";
});

document.addEventListener("dragover", function (e) {
  var zone = e.target.closest(".chart-drop-zone");
  if (zone) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
    zone.classList.add("chart-drop-zone--active");
  }
});

document.addEventListener("dragleave", function (e) {
  var zone = e.target.closest(".chart-drop-zone");
  if (zone && !zone.contains(e.relatedTarget)) {
    zone.classList.remove("chart-drop-zone--active");
  }
});

document.addEventListener("drop", function (e) {
  var zone = e.target.closest(".chart-drop-zone");
  if (!zone) return;
  e.preventDefault();
  zone.classList.remove("chart-drop-zone--active");

  var metric = e.dataTransfer.getData("text/plain");
  if (!metric) return;

  // Store metric globally so the clientside callback can read it.
  window._droppedMetric = metric;

  // Trigger Dash by clicking the hidden button.
  var btn = document.getElementById("_drop-btn");
  if (btn) btn.click();
});
