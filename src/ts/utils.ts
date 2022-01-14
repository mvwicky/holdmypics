import type { MakeEndpointArgs } from "./types";

export function getAttrs(element: HTMLElement): Record<string, string> {
  const attrs: Record<string, string> = {};
  for (const attr of element.attributes) {
    attrs[attr.name] = attr.value;
  }
  return attrs;
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

export function isEndpointArgs(
  input: {
    [k: string]: string;
  } | null
): input is MakeEndpointArgs {
  return input !== null && ARGS.every((key) => key in input);
}
