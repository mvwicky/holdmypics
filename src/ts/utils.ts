export function truthy<T>(input: T | null | undefined): input is T {
  return input !== null && input !== undefined;
}

export function elemIsTag<K extends keyof HTMLElementTagNameMap>(
  elem: Node | null | undefined,
  tag: K
): elem is HTMLElementTagNameMap[K] {
  return elem?.nodeName?.toUpperCase() === tag.toUpperCase();
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
