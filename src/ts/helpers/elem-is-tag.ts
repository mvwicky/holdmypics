export function elemIsTag<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  elem: Node | null | undefined
): elem is HTMLElementTagNameMap[K] {
  return elem?.nodeName?.toUpperCase() === tag.toUpperCase();
}
