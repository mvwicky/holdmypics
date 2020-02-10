interface MakeEndpointArgs {
  [k: string]: string;
  width: string;
  height: string;
  bg: string;
  fg: string;
  fmt: string;
  imageText: string;
  font: string;
  seed: string;
}

interface AnyFunc {
  (...args: any[]): any;
}
declare const PRODUCTION: boolean;

declare module "*.svg" {
  const value: string;
  export default value;
}

interface InputCallbackArgs {
  form: HTMLFormElement;
  endpoint: HTMLElement;
  btn: HTMLElement;
  image: HTMLImageElement;
  id: string;
}
