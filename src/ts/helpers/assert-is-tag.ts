import { elemIsTag } from "./elem-is-tag";
import type { TagMap } from "./elem-is-tag";

export function assertIsTag<K extends keyof TagMap>(
  elem: Node,
  tag: K
): asserts elem is TagMap[K] {
  if (!elemIsTag(elem, tag)) {
    throw new Error(
      `Expected element to be ${tag}, got ${elem.nodeName.toLowerCase()}`
    );
  }
}
