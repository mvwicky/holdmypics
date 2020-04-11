import checkSvg from "../icons/check.svg";
import copySvg from "../icons/copy.svg";

import { truthy, getAttrs } from "./utils";

const ICON_CONTENTS: Map<string, string> = new Map([
  ["check", checkSvg],
  ["copy", copySvg],
]);

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

export function replaceIcons() {
  document
    .querySelectorAll<HTMLElement>("[data-icon]")
    .forEach(replaceIcon.bind(null));
}
