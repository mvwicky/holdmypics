import { FormInput } from "../types";
import { elemIsTag } from "./elem-is-tag";

const checks = [elemIsTag.bind(null, "input"), elemIsTag.bind(null, "select")];

export function isInput(e: Element): e is FormInput {
  return checks.some((f) => f(e));
}

export function gatherParams(
  f: HTMLFormElement
): Record<string, string> | null {
  const params: { [k: string]: string } = {};
  const n = f.elements.length;
  for (const elem of f.elements) {
    if (isInput(elem)) {
      if (elem.checkValidity()) {
        if (elem.type === "checkbox" && elemIsTag("input", elem)) {
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
