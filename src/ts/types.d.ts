export type FormInput = HTMLInputElement | HTMLSelectElement;
export type NodeMaybe = Node | null | undefined;

export interface MakeEndpointArgs {
  [k: string]: string;
  width: string;
  height: string;
  bg: string;
  fg: string;
  fmt: string;
  imageText: string;
  font: string;
  seed: string;
  randomText: string;
}

export interface EndpointPathArgs {
  width: string;
  height: string;
  bg: string;
  fg: string;
  fmt: string;
}

interface EndpointQueryArgs {
  imageText: string;
  font: string;
  seed: string;
  randomText: boolean;
}

interface EndpointArgs {
  path: EndpointPathArgs;
  query: EndpointQueryArgs;
}

declare const PRODUCTION: boolean;

export interface InputCallbackArgs {
  btn: HTMLElement;
  endpoint: HTMLElement;
  form: HTMLFormElement;
  id: string;
  image: HTMLImageElement;
}
