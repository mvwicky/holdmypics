import "../scss/main.scss";

import { rIC } from "./dom/idle";
import { assertIsTag } from "./helpers/assert-is-tag";
import { debounce } from "./helpers/debounce";
import { elemIsTag } from "./helpers/elem-is-tag";
import { replaceIcons } from "./icons";
import { log } from "./log";

function getClipboard() {
  return import(/* webpackChunkName: "clipboard" */ "clipboard");
}

function getTippy() {
  return import(/* webpackChunkName: "tippy" */ "tippy.js");
}

function getRand() {
  return import(
    /* webpackChunkName: "random-text" */
    /* webpackMode: "eager" */
    "./random-text"
  );
}

const ARGS: readonly string[] = [
  "width",
  "height",
  "bg",
  "fg",
  "fmt",
  "imageText",
  "font",
];

function isEndpointArgs(
  input: Record<string, string> | null
): input is MakeEndpointArgs {
  return input !== null && ARGS.every((key) => key in input);
}

function makeEndpoint(args: MakeEndpointArgs) {
  const {
    width,
    height,
    bg,
    fg,
    fmt,
    imageText,
    font,
    seed,
    randomText,
  } = args;
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
  if (randomText) {
    url.searchParams.append("random_text", "");
  }
  return url;
}

const checks = [elemIsTag.bind(null, "input"), elemIsTag.bind(null, "select")];

function isInput(e: Element): e is FormInput {
  return checks.some((f) => f(e));
}

function gatherParams(f: HTMLFormElement): Record<string, string> | null {
  const params: { [k: string]: string } = {};
  const n = f.elements.length;
  for (let i = 0; i < n; i++) {
    const elem = f.elements[i];
    if (isInput(elem)) {
      if (elem.checkValidity()) {
        if (elem.type === "checkbox") {
          assertIsTag("input", elem);
          params[elem.id] = elem.checked ? "on" : "";
        } else {
          const value = elem.value;
          params[elem.id] = elem.disabled ? "" : value && value.trim();
        }
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
  log(JSON.stringify(params, undefined, 2));
  if (isEndpointArgs(params)) {
    log(`Good parameters`);
    const url = makeEndpoint(params);
    args.endpoint.textContent = url.pathname + url.search;
    if (elemIsTag("a", args.endpoint)) {
      args.endpoint.href = url.pathname + url.search;
    }
    args.btn.dataset.clipboardText = url.href;
    if (!["width", "height"].includes(args.id)) {
      args.image.src = url.href;
    }
  }
}

async function main(this: Document) {
  const exampleImage = this.getElementById("example-image");
  if (!elemIsTag("img", exampleImage)) {
    return;
  }
  const endpoint = this.getElementById("endpoint-url");
  if (!endpoint) {
    return;
  }
  const btn = this.getElementById("copy-button");
  if (!elemIsTag("button", btn)) {
    return;
  }
  const form = this.getElementById("params-form");
  if (!elemIsTag("form", form)) {
    return;
  }

  rIC(() => initIcons(btn), { timeout: 3000 });

  const initialParams = gatherParams(form);
  if (isEndpointArgs(initialParams)) {
    rIC(() => (btn.dataset.clipboardText = makeEndpoint(initialParams).href), {
      timeout: 3000,
    });
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

  (await getRand()).initRandomText();
}

function initIcons(btn: HTMLButtonElement) {
  replaceIcons().then(() => {
    const copyIconEl = btn.querySelector<HTMLElement>(".feather-copy");
    const checkIconEl = btn.querySelector<HTMLElement>(".feather-check");
    if (copyIconEl && checkIconEl) {
      log("Everything seems to exist.");
    }
    afterFeather(btn);
  });
}

async function afterFeather(copyBtn: HTMLButtonElement) {
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
      });
      copyBtn.onanimationstart = (event: AnimationEvent) => {
        log(`Start: ${event.animationName}`);
      };
      copyBtn.onanimationend = (event: AnimationEvent) => {
        log(`End: ${event.animationName}`);
        tip.hide();
        copyBtn.classList.remove("just-copied");
      };
      const copy = new Clipboard(copyBtn);
      copy.on("success", () => {
        tip.show();
        copyBtn.classList.add("just-copied");
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
