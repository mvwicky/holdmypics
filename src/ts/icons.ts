import checkSvg from "Feather/check.svg";
import copySvg from "Feather/copy.svg";
import refreshCwSvg from "Feather/refresh-cw.svg";

import { truthy, getAttrs } from "./utils";
import { log } from "./log";

const ICON_CONTENTS: Map<string, string> = new Map([
  ["check", checkSvg],
  ["copy", copySvg],
  ["refresh-cw", refreshCwSvg],
]);

function replaceIcon(element: HTMLElement) {
  const attrs = getAttrs(element);
  const iconName = attrs["data-icon"];
  delete attrs["data-icon"];
  delete attrs["class"];
  const cts = ICON_CONTENTS.get(iconName);
  if (truthy(cts)) {
    log(`Replacing ${iconName}`);
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

export function replaceIcons() {
  document
    .querySelectorAll<HTMLElement>("[data-icon]")
    .forEach(replaceIcon.bind(null));
}
