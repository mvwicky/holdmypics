export type TagMap = HTMLElementTagNameMap;

export function elemIsTag<K extends keyof TagMap>(
  elem: Node | null | undefined,
  tag: K
): elem is TagMap[K] {
  return elem?.nodeName?.toUpperCase() === tag.toUpperCase();
}
