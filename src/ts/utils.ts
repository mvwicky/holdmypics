type TagMap = HTMLElementTagNameMap;

export function truthy<T>(input: T | null | undefined): input is T {
  return input !== null && input !== undefined;
}

function elemIsTag<K extends keyof TagMap>(
  elem: Node | null | undefined,
  tag: K
): elem is TagMap[K] {
  return elem?.nodeName?.toUpperCase() === tag.toUpperCase();
}

function assertIsTag<K extends keyof TagMap>(
  elem: Node,
  tag: K
): asserts elem is TagMap[K] {
  if (!elemIsTag(elem, tag)) {
    throw new Error(
      `Expected element to be ${tag}, got ${elem.nodeName.toLowerCase()}`
    );
  }
}

export function getAttrs(element: HTMLElement): Record<string, string> {
  return Array.from(element.attributes).reduce((attrs, attr) => {
    attrs[attr.name] = attr.value;
    return attrs;
  }, {} as Record<string, string>);
}

const ARGS = ["width", "height", "bg", "fg", "fmt", "imageText", "font"];

export function isEndpointArgs(input: {
  [k: string]: string;
}): input is MakeEndpointArgs {
  return ARGS.every((key) => key in input);
}

export { elemIsTag, assertIsTag };
