import "./styles.scss";

function truthy<T>(input: T | null | undefined): input is T {
  return input !== null && input !== undefined;
}

function isInput(input: Element | RadioNodeList): input is HTMLInputElement {
  return "checkValidity" in input;
}

const ARGS = ["width", "height", "bg", "fg", "fmt", "imageText", "font"];

function isEndpointArgs(input: {
  [k: string]: string;
}): input is MakeEndpointArgs {
  return ARGS.every(key => key in input);
}

(function(doc: Document, global: typeof globalThis) {
  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }

  function makeEndpoint(args: MakeEndpointArgs) {
    const { width, height, bg, fg, fmt, imageText, font, seed } = args;
    const path = `/api/${width}x${height}/${bg}/${fg}/${fmt}/`;
    const url = new URL(path, global.location.href);
    url.search = "";
    if (imageText) {
      url.searchParams.append("text", imageText);
    }
    if (font) {
      url.searchParams.append("font", font);
    }
    if (seed) {
      url.searchParams.append("seed", seed);
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

  function debounce<F extends AnyFunc>(
    func: F,
    wait: number = 250,
    immediate: boolean = false
  ) {
    let timeout: number | undefined;

    return function debouncedFunction(this: ThisType<F>, ...a: Parameters<F>) {
      const context = this;

      const later = function() {
        timeout = undefined;
        if (!immediate) {
          func.apply(context, a);
        }
      };
      const callNow = immediate && !timeout;
      window.clearTimeout(timeout);

      timeout = window.setTimeout(later, wait);
      if (callNow) {
        func.apply(context, a);
      }
    };
  }

  function main() {
    const exampleImage = doc.querySelector<HTMLImageElement>("#example-image");
    if (!truthy(exampleImage)) {
      return;
    }
    const endpoint = doc.getElementById("endpoint");
    if (!truthy(endpoint)) {
      return;
    }
    const btn = doc.getElementById("copy-button");
    if (!truthy(btn)) {
      return;
    }
    const form = doc.querySelector("form");
    if (!truthy(form)) {
      return;
    }

    getFeather().then(feather => {
      feather.replace();
      const copyIconEl = btn.querySelector<HTMLElement>(".feather-copy");
      const checkIconEl = btn.querySelector<HTMLElement>(".feather-check");
      if (truthy(copyIconEl) && truthy(checkIconEl)) {
        afterFeather(btn, copyIconEl, checkIconEl);
      }
    });

    console.log("Everything seems to exist.");

    const initialParams = gatherParams(form);
    if (truthy(initialParams) && isEndpointArgs(initialParams)) {
      const url = makeEndpoint(initialParams);
      btn.dataset.clipboardText = url.href;
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
          endpoint.textContent = url.pathname + url.search;
        }
        if (truthy(btn)) {
          btn.dataset.clipboardText = url.href;
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

function afterFeather(
  copyBtn: HTMLElement,
  copyIcon: HTMLElement,
  checkIcon: HTMLElement
) {
  console.log("Check and copy icons exist.");
  getClipboard().then(({ default: Clipboard }) => {
    const copy = new Clipboard(copyBtn);
    copy.on("success", () => {
      copyIcon.style.display = "none";
      checkIcon.style.display = "inline-flex";
      copyBtn.dataset.balloonPos = "up";
      copyBtn.dataset.balloonVisible = "";
      window.setTimeout(() => {
        checkIcon.style.display = "none";
        copyIcon.style.display = "inline-flex";
        delete copyBtn.dataset.balloonPos;
        delete copyBtn.dataset.balloonVisible;
      }, 1500);
    });
  });
}

function getClipboard() {
  return import(/* webpackChunkName: "clipboard" */ "clipboard");
}

function getFeather() {
  return import(/* webpackChunkName: "feather" */ "feather-icons");
}
