import "../scss/main.scss";

import { truthy, elemIsTag } from "./utils";
import { debounce } from "./debounce";
import { replaceIcons } from "./icons";
import { rIC } from "./idle";

const log = PRODUCTION ? (...args: any[]) => {} : console.log.bind(console);

function getVendoredStyles() {
  // return import(/* webpackChunkName: "vendors" */ "../scss/_vendor.scss");
}

function getClipboard() {
  return import(/* webpackChunkName: "clipboard" */ "clipboard");
}

function getTippy() {
  return import(/* webpackChunkName: "tippy" */ "tippy.js");
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
  const params: { [k: string]: string } = {};
  const n = f.elements.length;
  for (let i = 0; i < n; i++) {
    const elem = f.elements[i];
    if (elemIsTag(elem, "input") || elemIsTag(elem, "select")) {
      if (elem.checkValidity()) {
        const value = elem.value;
        params[elem.id] = value && value.trim();
      } else {
        return null;
      }
    }
  }
  return params;
}

function inputCallback(args: InputCallbackArgs) {
  log(`Input ${args.id} changed.`);
  const params = gatherParams(args.form);
  log(params);
  if (truthy(params) && isEndpointArgs(params)) {
    log(`Good parameters`);
    const url = makeEndpoint(params);
    args.endpoint.textContent = url.pathname + url.search;
    args.btn.dataset.clipboardText = url.href;
    if (!["width", "height"].includes(args.id)) {
      args.image.src = url.href;
    }
  }
}

async function main(this: Document) {
  const exampleImage = this.getElementById("example-image");
  if (!elemIsTag(exampleImage, "img")) {
    return;
  }
  const endpoint = this.getElementById("endpoint");
  if (!truthy(endpoint)) {
    return;
  }
  const btn = this.getElementById("copy-button");
  if (!elemIsTag(btn, "button")) {
    return;
  }
  const form = this.getElementById("params-form");
  if (!elemIsTag(form, "form")) {
    return;
  }

  rIC(() => initIcons(btn), { timeout: 3000 });

  const initialParams = gatherParams(form);
  if (truthy(initialParams) && isEndpointArgs(initialParams)) {
    rIC(
      () => {
        const url = makeEndpoint(initialParams);
        btn.dataset.clipboardText = url.href;
      },
      { timeout: 3000 }
    );
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

function initIcons(btn: HTMLButtonElement) {
  replaceIcons();
  const copyIconEl = btn.querySelector<HTMLElement>(".feather-copy");
  const checkIconEl = btn.querySelector<HTMLElement>(".feather-check");
  if (truthy(copyIconEl) && truthy(checkIconEl)) {
    afterFeather(btn, copyIconEl, checkIconEl);
  }
  log("Everything seems to exist.");
}

async function afterFeather(
  copyBtn: HTMLButtonElement,
  copyIcon: HTMLElement,
  checkIcon: HTMLElement
) {
  const { default: tippy, roundArrow } = await getTippy();
  const { default: Clipboard } = await getClipboard();
  rIC(
    () => {
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
      const copy = new Clipboard(copyBtn);
      copy.on("success", () => {
        tip.show();
        window.setTimeout(() => {
          tip.hide();
        }, 1500);
      });
      log("Check and copy icons exist.");
      copyBtn.disabled = false;
    },
    { timeout: 3000 }
  );
}

(function (d: Document, global: Window) {
  if (d.readyState === "loading") {
    d.addEventListener("DOMContentLoaded", main);
  } else {
    main.bind(d)();
  }
})(document, window);

declare global {
  interface Window {
    requestIdleCallback: (
      callback: (deadline: RequestIdleCallbackDeadline) => void,
      opts?: RequestIdleCallbackOptions
    ) => RequestIdleCallbackHandle;
    cancelIdleCallback: (handle: RequestIdleCallbackHandle) => void;
  }
}
