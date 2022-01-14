import { elemIsTag } from "./elem-is-tag";

export function assertIsTag<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  elem: Node
): asserts elem is HTMLElementTagNameMap[K] {
  if (!elemIsTag(tag, elem)) {
    throw new Error(
      `Expected element to be ${tag}, got ${elem.nodeName.toLowerCase()}`
    );
  }
}
