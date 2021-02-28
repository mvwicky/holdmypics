import type { MakeEndpointArgs } from "./types";

export function getAttrs(element: HTMLElement): Record<string, string> {
  return Array.from(element.attributes).reduce((attrs, attr) => {
    attrs[attr.name] = attr.value;
    return attrs;
  }, {} as Record<string, string>);
}

const ARGS = [
  "width",
  "height",
  "bg",
  "fg",
  "fmt",
  "imageText",
  "font",
] as const;

export function isEndpointArgs(input: {
  [k: string]: string;
}): input is MakeEndpointArgs {
  return ARGS.every((key) => key in input);
}
