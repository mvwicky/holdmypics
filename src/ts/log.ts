declare const PRODUCTION: boolean;

const styles = [
  "border-radius: 0.3em;",
  "font-weight: 700;",
  "padding: 2px 0.33em;",
  "background-color: #1273d7;",
  "color: #fff;",
].join(" ");

function makeLogger(): (...args: any[]) => void {
  const func = PRODUCTION ? "debug" : "log";
  return console[func].bind(console, "%c[holdmypics]", styles);
}
export const log = makeLogger();
