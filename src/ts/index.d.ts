type RequestIdleCallbackHandle = any;
type RequestIdleCallbackOptions = {
  timeout?: number;
};
type RequestIdleCallbackDeadline = {
  readonly didTimeout: boolean;
  timeRemaining: () => number;
};

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
  randomText: string;
}

interface EndpointPathArgs {
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

interface AnyFunc {
  (...args: any[]): any;
}
declare const PRODUCTION: boolean;

declare module "*.svg" {
  const value: string;
  export default value;
}

interface InputCallbackArgs {
  btn: HTMLElement;
  endpoint: HTMLElement;
  form: HTMLFormElement;
  id: string;
  image: HTMLImageElement;
}
