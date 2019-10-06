interface MakeEndpointArgs {
  [k: string]: string;
  width: string;
  height: string;
  bg: string;
  fg: string;
  fmt: string;
  imageText: string;
  font: string;
}

interface AnyFunc {
  (...args: any[]): any;
}
