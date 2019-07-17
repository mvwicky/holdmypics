/*global
  browser, feather
*/

"use strict";

(function(global, doc) {
  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", () => {
      main();
    });
  } else {
    main();
  }

  function makeEndpoint({ width, height, bg, fg, fmt, imageText, font }) {
    const path = `/api/${width}x${height}/${bg}/${fg}/${fmt}/`;
    const url = new URL(window.location.href);
    url.pathname = path;
    url.search = "";
    if (imageText) {
      url.searchParams.append("text", imageText);
    }
    if (font) {
      url.searchParams.append("font", font);
    }
    return url;
  }

  function debounce(func, wait = 250, immediate = false) {
    let timeout;

    return function debouncedFunction(...a) {
      let context = this;
      let args = Array.from(arguments);

      let later = function() {
        timeout = undefined;
        if (!immediate) {
          func.apply(context, ...args);
        }
      };
      let callNow = immediate && !timeout;
      clearTimeout(timeout);

      timeout = setTimeout(later, wait);
      if (callNow) {
        func.apply(context, ...args);
      }
    };
  }

  function main() {
    feather.replace();

    const exampleImage = doc.getElementById("example-image");
    const endpoint = doc.getElementById("endpoint");
    const copyButton = doc.getElementById("copy-button");
    const form = doc.querySelector("form");

    const initialParams = gatherParams(form);
    const url = makeEndpoint(initialParams);
    copyButton.dataset.url = url.href;
    if ("clipboard" in navigator) {
      copyButton.addEventListener("click", () => {
        navigator.clipboard.writeText(copyButton.dataset.url).then(
          () => {
            console.log("Wrote text");
          },
          () => {
            console.log("Failed to write text.");
          }
        );
      });
    }

    const elements = form.elements;
    for (let i = 0; i < elements.length; i++) {
      function inputCallback() {
        const params = gatherParams(form);
        if (params !== null) {
          const url = makeEndpoint(params);
          endpoint.textContent = `${url.pathname}${url.search}`;
          copyButton.dataset.url = url.href;
        }
      }
      elements[i].addEventListener("input", debounce(inputCallback, 1000));
    }
  }
  function gatherParams(f) {
    const elems = f.elements;
    const params = {};
    for (let j = 0; j < elems.length; j++) {
      const id = elems[j].id;
      if (elems[j].checkValidity()) {
        params[id] = elems[j].value;
      } else {
        return null;
      }
    }
    return params;
  }
})(window, document);
