import "./scss/main.scss";

import checkSvg from "./icons/check.svg";
import copySvg from "./icons/copy.svg";

const log = PRODUCTION ? (...args: any[]) => {} : console.log.bind(console);

const ICON_CONTENTS: Map<string, string> = new Map([
  ["check", checkSvg],
  ["copy", copySvg],
]);

function getClipboard() {
  return import(/* webpackChunkName: "clipboard" */ "clipboard");
}

function getTippy() {
  return import(/* webpackChunkName: "tippy" */ "tippy.js");
}

function truthy<T>(input: T | null | undefined): input is T {
  return input !== null && input !== undefined;
}

function isInput(input: Element | RadioNodeList): input is HTMLInputElement {
  return "checkValidity" in input;
}

function getAttrs(element: HTMLElement): Record<string, string> {
  return Array.from(element.attributes).reduce((attrs, attr) => {
    attrs[attr.name] = attr.value;
    return attrs;
  }, {} as Record<string, string>);
}

function replaceIcons() {
  const toReplace = document.querySelectorAll<HTMLElement>("[data-icon]");
  Array.from(toReplace, (element) => {
    replaceIcon(element);
  });
}

function replaceIcon(element: HTMLElement) {
  const attrs = getAttrs(element);
  const iconName = attrs["data-icon"];
  delete attrs["data-icon"];
  delete attrs["class"];
  const cts = ICON_CONTENTS.get(iconName);
  if (truthy(cts)) {
    const svgDoc = new DOMParser().parseFromString(cts, "image/svg+xml");
    const svgElem = svgDoc.querySelector("svg");
    if (truthy(svgElem)) {
      const classes = Array.from(element.classList);
      svgElem.classList.add.apply(svgElem.classList, classes);
      Object.entries(attrs).forEach(([name, value]) => {
        svgElem.setAttribute(name, value);
      });
      element.parentNode?.replaceChild(svgElem, element);
    }
  }
}

const ARGS = ["width", "height", "bg", "fg", "fmt", "imageText", "font"];

function isEndpointArgs(input: {
  [k: string]: string;
}): input is MakeEndpointArgs {
  return ARGS.every((key) => key in input);
}

function makeEndpoint(args: MakeEndpointArgs) {
  const { width, height, bg, fg, fmt, imageText, font, seed } = args;
  const path = `/api/${width}x${height}/${bg}/${fg}/${fmt}/`;
  const url = new URL(path, window.location.href);
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

    const later = function () {
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

async function main() {
  const exampleImage = document.querySelector<HTMLImageElement>(
    "#example-image"
  );
  if (!truthy(exampleImage)) {
    return;
  }
  const endpoint = document.getElementById("endpoint");
  if (!truthy(endpoint)) {
    return;
  }
  const btn = document.getElementById("copy-button");
  if (!truthy(btn)) {
    return;
  }
  const form = document.querySelector("form");
  if (!truthy(form)) {
    return;
  }

  replaceIcons();
  const copyIconEl = btn.querySelector<HTMLElement>(".feather-copy");
  const checkIconEl = btn.querySelector<HTMLElement>(".feather-check");
  if (truthy(copyIconEl) && truthy(checkIconEl)) {
    afterFeather(btn, copyIconEl, checkIconEl);
  }
  log("Everything seems to exist.");

  const initialParams = gatherParams(form);
  if (truthy(initialParams) && isEndpointArgs(initialParams)) {
    const url = makeEndpoint(initialParams);
    btn.dataset.clipboardText = url.href;
  }

  function inputCallback(args: InputCallbackArgs) {
    const params = gatherParams(args.form);
    if (truthy(params) && isEndpointArgs(params)) {
      const url = makeEndpoint(params);
      args.endpoint.textContent = url.pathname + url.search;
      args.btn.dataset.clipboardText = url.href;
      if (!["width", "height"].includes(args.id)) {
        args.image.src = url.href;
      }
    }
  }
  const elements = form.elements;
  const numElements = form.elements.length;
  for (let i = 0; i < numElements; i++) {
    const args: InputCallbackArgs = {
      form,
      endpoint,
      btn,
      image: exampleImage,
      id: elements[i].id,
    };
    const cb = debounce(inputCallback.bind(null, args), 750);
    elements[i].addEventListener("input", cb);
  }
}

async function afterFeather(
  copyBtn: HTMLElement,
  copyIcon: HTMLElement,
  checkIcon: HTMLElement
) {
  const { default: tippy, roundArrow } = await getTippy();
  const { default: Clipboard } = await getClipboard();
  const tip = tippy(copyBtn, {
    trigger: "manual",
    ignoreAttributes: true,
    content: "Copied to Clipboard",
    theme: "light light-border clipboard-tooltip",
    arrow: roundArrow,
    offset: [0, 12],
    animation: "shift-away",
    onHidden: () => {
      window.requestAnimationFrame(() => {
        checkIcon.classList.add("d-none");
        copyIcon.classList.remove("d-none");
      });
    },
    onShow: () => {
      window.requestAnimationFrame(() => {
        checkIcon.classList.remove("d-none");
        copyIcon.classList.add("d-none");
      });
    },
  });
  log("Check and copy icons exist.");
  const copy = new Clipboard(copyBtn);
  copy.on("success", () => {
    tip.show();
    window.setTimeout(() => {
      tip.hide();
    }, 1500);
  });
}

(function (d: Document, global: Window) {
  if (d.readyState === "loading") {
    d.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})(document, window);
