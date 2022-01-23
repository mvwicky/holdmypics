import "../css/main.css";

import { rIC } from "./dom/idle";
import { elemIsTag } from "./helpers/elem-is-tag";
import { replaceIcons } from "./icons";
import { log } from "./log";

function getClipboard() {
  return import("clipboard");
}

interface PageModule {
  initPage: () => void;
}

async function main(this: Document) {
  this.removeEventListener("DOMContentLoaded", main);
  const { pathname: path } = this.location;
  const routes: [RegExp, () => Promise<PageModule>][] = [
    [/\/tiled\//, () => import("./pages/tiled_page")],
    [/(\/|.*)/, () => import("./pages/index_page")],
  ];
  for (const [re, importFunc] of routes) {
    if (re.test(path)) {
      log(`Matched ${path}`);
      const { initPage } = await importFunc();
      initPage();
      break;
    }
  }

  const btn = this.getElementById("copy-button");
  if (elemIsTag("button", btn)) {
    rIC(() => initIcons(btn), { timeout: 3000 });
  }
}

function initIcons(btn: HTMLButtonElement) {
  replaceIcons().then(() => {
    const copyIconEl = btn.querySelector<HTMLElement>(".feather-copy");
    const checkIconEl = btn.querySelector<HTMLElement>(".feather-check");
    if (copyIconEl && checkIconEl) {
      log("Check and copy icons exist.");
    }
    afterFeather(btn);
  });
}

async function afterFeather(copyBtn: HTMLButtonElement) {
  const { default: Clipboard } = await getClipboard();
  log("Loaded clipboard.");
  const setJustCopied = (on: boolean) => {
    const func = on ? "add" : "remove";
    copyBtn.classList[func]("just-copied");
  };
  self.setTimeout(() => {
    const timeoutId: number | undefined = undefined;
    copyBtn.onanimationend = (event: AnimationEvent) => {
      self.clearTimeout(timeoutId);
      setJustCopied(false);
    };
    const copy = new Clipboard(copyBtn);
    copy.on("success", () => {
      self.setTimeout(() => setJustCopied(false), 1500);
      setJustCopied(true);
    });
    copyBtn.disabled = false;
  });
}

(function (d: Document, global: Window) {
  if (d.readyState === "loading") {
    d.addEventListener("DOMContentLoaded", main);
  } else {
    main.bind(d)();
  }
})(document, window);
