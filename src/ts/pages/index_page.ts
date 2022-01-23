import { rIC } from "../dom/idle";
import { debounce } from "../helpers/debounce";
import { elemIsTag } from "../helpers/elem-is-tag";
import { gatherParams } from "../helpers/forms";
import { log } from "../log";
import type { InputCallbackArgs, MakeEndpointArgs } from "../types";
import { isEndpointArgs } from "../utils";

function getRand() {
  return import("../helpers/random-text");
}

function makeEndpoint(args: MakeEndpointArgs) {
  const { width, height, bg, fg, fmt, imageText, font, seed, randomText } =
    args;
  const path = `/api/${width}x${height}/${bg}/${fg}/${fmt}/`;
  const url = new URL(path, self.location.href);
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

function inputCallback(args: InputCallbackArgs) {
  log(`Input ${args.id} changed.`);
  const params = gatherParams(args.form);
  log(JSON.stringify(params, undefined, 2));
  if (isEndpointArgs(params)) {
    log(`Good parameters`);
    const url = makeEndpoint(params);
    const fullPath = url.pathname + url.search;
    args.endpoint.textContent = fullPath;
    if (elemIsTag("a", args.endpoint)) {
      args.endpoint.href = fullPath;
    }
    args.btn.dataset.clipboardText = url.href;
    if (!["width", "height"].includes(args.id)) {
      args.image.src = url.href;
    }
  }
}

export async function initPage() {
  const exampleImage = document.getElementById("example-image");
  if (!elemIsTag("img", exampleImage)) {
    return;
  }
  const endpoint = document.getElementById("endpoint-url");
  if (!endpoint) {
    return;
  }
  const btn = document.getElementById("copy-button");
  if (!elemIsTag("button", btn)) {
    return;
  }
  const form = document.getElementById("params-form");
  if (!elemIsTag("form", form)) {
    return;
  }

  const initialParams = gatherParams(form);
  if (isEndpointArgs(initialParams)) {
    rIC(() => (btn.dataset.clipboardText = makeEndpoint(initialParams).href), {
      timeout: 1000,
    });
  }

  const { elements } = form;
  const numElements = elements.length;
  for (let i = 0; i < numElements; i++) {
    const args: InputCallbackArgs = {
      form,
      endpoint,
      btn,
      image: exampleImage,
      id: elements[i].id,
    };
    const cb = debounce(inputCallback.bind(null, args), 500);
    elements[i].addEventListener("input", cb);
  }

  (await getRand()).initRandomText();
}
