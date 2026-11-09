/**
 * Click-to-zoom for Mermaid diagrams.
 *
 * Zensical's bundle draws each diagram into a closed shadow root, out of reach
 * of page scripts. It draws with the global `mermaid.render`, which is the
 * theme's copy of Mermaid, and hands the filled shadow root to the
 * `bindFunctions` of the result. This script wraps both to learn the element
 * and the SVG of each diagram, makes the element a button and opens a copy of
 * the SVG in GLightbox. The copy sits in a shadow root of its own and takes
 * the theme colors from the CSS variables of the page, so it follows the color
 * scheme. main.html loads this script after Mermaid and GLightbox, on pages
 * with a diagram.
 */
(function () {
  "use strict";

  if (typeof mermaid === "undefined" || typeof GLightbox === "undefined") return;

  /**
   * Styles of the copy: as large as the screen allows, but at least the size
   * Mermaid drew and at most twice that. A larger diagram scrolls. Only the
   * outer SVG: icons in architecture diagrams are nested SVGs.
   */
  var VIEW_STYLE =
    "<style>" +
    ":host{display:block;overflow:auto;max-width:calc(94vw - 40px);max-height:calc(90vh - 40px)}" +
    ":host>svg{display:block;height:auto;max-width:none!important;" +
    "width:clamp(var(--width),min(94vw - 40px,(90vh - 40px) * var(--ratio)),var(--width) * 2)}" +
    "</style>";

  /** Element that shows a copy of the diagram SVG, sized from its viewBox; it takes focus so keys scroll it. */
  function createView(svg) {
    var view = document.createElement("div");
    view.className = "md-typeset iscc-diagram-view";
    view.tabIndex = -1;
    var root = view.attachShadow({ mode: "open" });
    root.innerHTML = VIEW_STYLE + svg;
    var box = root.querySelector("svg").viewBox.baseVal;
    view.style.setProperty("--width", box.width + "px");
    view.style.setProperty("--ratio", String(box.width / box.height));
    return view;
  }

  /**
   * Open a copy of the diagram SVG in a lightbox. The copy takes focus, since
   * GLightbox keeps Tab on its buttons; focus returns to the diagram on close.
   */
  function openView(host, svg) {
    var view = createView(svg);
    GLightbox({
      elements: [{ content: view, width: "auto", height: "auto" }],
      touchNavigation: false,
      draggable: false,
      zoomable: false,
      openEffect: "zoom",
      closeEffect: "zoom",
      onOpen: function () {
        view.focus({ preventScroll: true });
      },
      onClose: function () {
        host.focus({ preventScroll: true });
      },
    }).open();
  }

  /** Make a drawn diagram open in a lightbox on click, Enter or Space; links in it still work. */
  function makeZoomable(root, svg) {
    var host = root.host;
    host.classList.add("iscc-diagram");
    host.setAttribute("role", "button");
    host.setAttribute("tabindex", "0");
    host.setAttribute("aria-label", "Enlarge diagram");
    root.addEventListener("click", function (event) {
      if (event.target.closest("a")) event.stopPropagation();
    });
    host.addEventListener("click", function () {
      openView(host, svg);
    });
    host.addEventListener("keydown", function (event) {
      // root.activeElement is a focused link in the diagram, which keeps its keys
      if ((event.key !== "Enter" && event.key !== " ") || root.activeElement) return;
      event.preventDefault();
      openView(host, svg);
    });
  }

  var render = mermaid.render;

  /** Mermaid's render, which also hands each drawn diagram to makeZoomable. */
  mermaid.render = function () {
    return render.apply(this, arguments).then(function (result) {
      var bind = result.bindFunctions;
      return Object.assign({}, result, {
        bindFunctions: function (root) {
          if (bind) bind(root);
          makeZoomable(root, result.svg);
        },
      });
    });
  };
})();
