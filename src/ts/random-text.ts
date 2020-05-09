import { elemIsTag } from "./helpers/elem-is-tag";

export function initRandomText() {
  const txtInp = document.getElementById("imageText");
  const randInp = document.getElementById("randomText");
  if (elemIsTag(txtInp, "input") && elemIsTag(randInp, "input")) {
    addListener(txtInp, randInp);
  }
}

function addListener(textInp: HTMLInputElement, randomCheck: HTMLInputElement) {
  randomCheck.addEventListener("change", function (this) {
    textInp.disabled = this.checked;
  });
}
