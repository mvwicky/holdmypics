import { log } from "../log";
import { elemIsTag } from "./elem-is-tag";

export function initRandomText() {
  const txtInp = document.getElementById("imageText");
  const randInp = document.getElementById("randomText");
  if (elemIsTag("input", txtInp) && elemIsTag("input", randInp)) {
    addListener(txtInp, randInp);
  }
  log("Loaded random-text");
}

function addListener(textInp: HTMLInputElement, randomCheck: HTMLInputElement) {
  randomCheck.addEventListener("change", function (this) {
    textInp.disabled = this.checked;
  });
}
