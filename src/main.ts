import "../node_modules/balloon-css/src/balloon.scss";
import "../node_modules/sanitize.css/sanitize.css";
import "../node_modules/sanitize.css/typography.css";
import "../node_modules/sanitize.css/forms.css";

import feather from "feather-icons";

function truthy<T>(input: T | null | undefined): input is T {
  return input !== null && input !== undefined;
}

function isInput(input: Element | RadioNodeList): input is HTMLInputElement {
  return "checkValidity" in input;
}

function isEndpointArgs(input: {
  [k: string]: string;
}): input is MakeEndpointArgs {
  return ["width", "height", "bg", "fg", "fmt", "imageText", "font"].every(
    (key) => key in input
  );
}

(function(doc: Document, global: typeof globalThis) {
  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }

  function makeEndpoint(args: MakeEndpointArgs) {
    const { width, height, bg, fg, fmt, imageText, font } = args;
    const path = `/api/${width}x${height}/${bg}/${fg}/${fmt}/`;
    const url = new URL(global.location.href);
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

  function gatherParams(f: HTMLFormElement): { [k: string]: string } | null {
    const elems = f.elements;
    const params: { [k: string]: string } = {};
    for (let j = 0; j < elems.length; j++) {
      const elem = elems[j];
      if (isInput(elem)) {
        const id = elem.id;
        if (elem.checkValidity()) {
          const value = elem.value;
          if (value) {
            params[id] = value.trim();
          } else {
            params[id] = value;
          }
        } else {
          return null;
        }
      }
    }
    return params;
  }

  function debounce(
    func: AnyFunc,
    wait: number = 250,
    immediate: boolean = false
  ) {
    let timeout: number | undefined;

    return function debouncedFunction(...a: any[]) {
      //@ts-ignore
      let context: any = this;
      let args = Array.from(arguments);

      let later = function() {
        timeout = undefined;
        if (!immediate) {
          //@ts-ignore
          func.apply(context, ...args);
        }
      };
      let callNow = immediate && !timeout;
      clearTimeout(timeout);

      //@ts-ignore
      timeout = setTimeout(later, wait);
      if (callNow) {
        //@ts-ignore
        func.apply(context, ...args);
      }
    };
  }

  function main() {
    feather.replace();

    const exampleImage = doc.querySelector<HTMLImageElement>("#example-image");
    if (!truthy(exampleImage)) {
      return;
    }
    const endpoint = doc.getElementById("endpoint");
    if (!truthy(endpoint)) {
      return;
    }
    const copyButton = doc.getElementById("copy-button");
    if (!truthy(copyButton)) {
      return;
    }
    const form = doc.querySelector("form");
    if (!truthy(form)) {
      return;
    }

    const copyIconEl = copyButton.querySelector<HTMLElement>(".feather-copy");
    const checkIconEl = copyButton.querySelector<HTMLElement>(".feather-check");

    // const copy = new ClipboardJS(copyButton);
    if (truthy(copyIconEl) && truthy(checkIconEl)) {
      const copyIcon = copyIconEl;
      const checkIcon = checkIconEl;
      import("clipboard").then(({ default: Clipboard }) => {
        const copy = new Clipboard(copyButton);
        copy.on("success", () => {
          copyIcon.style.display = "none";
          checkIcon.style.display = "inline-flex";
          copyButton.dataset.balloonPos = "up";
          copyButton.dataset.balloonVisible = "";
          window.setTimeout(() => {
            checkIcon.style.display = "none";
            copyIcon.style.display = "inline-flex";
            delete copyButton.dataset.balloonPos;
            delete copyButton.dataset.balloonVisible;
          }, 2000);
        });
      });
    }

    const initialParams = gatherParams(form);
    if (truthy(initialParams) && isEndpointArgs(initialParams)) {
      const url = makeEndpoint(initialParams);
      copyButton.dataset.clipboardText = url.href;
    }

    const elements = form.elements;
    function inputCallback(i: number) {
      if (!truthy(form)) {
        return;
      }
      const params = gatherParams(form);
      if (truthy(params) && isEndpointArgs(params)) {
        const url = makeEndpoint(params);
        if (truthy(endpoint)) {
          endpoint.textContent = url.href;
        }
        if (truthy(copyButton)) {
          copyButton.dataset.clipboardText = url.href;
        }
        const id = elements[i].id;
        if (truthy(exampleImage) && !["width", "height"].includes(id)) {
          exampleImage.src = url.href;
        }
      }
    }
    for (let i = 0; i < elements.length; i++) {
      const cb = debounce(inputCallback.bind(null, i), 750);
      elements[i].addEventListener("input", cb);
    }
  }
})(document, window);
