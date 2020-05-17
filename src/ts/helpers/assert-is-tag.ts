import { elemIsTag } from "./elem-is-tag";
import type { TagMap } from "./elem-is-tag";

export function assertIsTag<K extends keyof TagMap>(
  tag: K,
  elem: Node
): asserts elem is TagMap[K] {
  if (!elemIsTag(tag, elem)) {
    throw new Error(
      `Expected element to be ${tag}, got ${elem.nodeName.toLowerCase()}`
    );
  }
}
