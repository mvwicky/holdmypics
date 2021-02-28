import type { NodeMaybe } from "../types";

export type TagMap = HTMLElementTagNameMap;

function elemIsTag<K extends keyof TagMap>(
  tag: K,
  elem: NodeMaybe
): elem is TagMap[K] {
  return elem?.nodeName?.toUpperCase() === tag.toUpperCase();
}

export { elemIsTag };
