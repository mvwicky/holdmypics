import { debounce } from "../helpers/debounce";
import { elemIsTag } from "../helpers/elem-is-tag";
import { log } from "../log";

function getInputById(id: string): HTMLInputElement | null {
  const inp = document.getElementById(id);
  return elemIsTag("input", inp) ? inp : null;
}

function makeURL(
  width: number,
  height: number,
  cols: number,
  rows: number,
  fmt: string,
  colors: string
): URL {
  const path = `/api/tiled/${width}x${height}/${cols}/${rows}/${fmt}/`;
  const url = new URL(path, self.location.href);
  if (colors) {
    for (const col of colors.split(",")) {
      url.searchParams.append("colors", col);
    }
  }
  return url;
}

export function initPage() {
  const exampleImage = document.getElementById("example-image");
  if (!elemIsTag("img", exampleImage)) {
    return;
  }

  const endpoint = document.getElementById("endpoint-url");
  if (!elemIsTag("a", endpoint)) {
    return;
  }

  const form = document.getElementById("params-form");
  if (!elemIsTag("form", form)) {
    return;
  }
  const [width, height] = [getInputById("width"), getInputById("height")];
  const [cols, rows] = [getInputById("cols"), getInputById("rows")];
  const colors = getInputById("colors");
  const fmt = document.getElementById("fmt");
  if (!elemIsTag("select", fmt)) {
    return;
  }
  if (!(width && height && cols && rows && colors)) {
    return;
  }
  log("Everything seems to exist.");

  const controls = [width, height, cols, rows, fmt, colors];
  for (const inp of controls) {
    inp.addEventListener(
      "input",
      debounce(() => {
        log(`${inp.id} changed.`);
        if (!form.checkValidity()) {
          log("Not valid!");
          return;
        }
        const url = makeURL(
          width.valueAsNumber,
          height.valueAsNumber,
          cols.valueAsNumber,
          rows.valueAsNumber,
          fmt.value,
          colors.value
        );
        const fullPath = url.pathname + url.search;
        log(fullPath);
        endpoint.textContent = fullPath;
        if (!["width", "height"].includes(inp.id)) {
          exampleImage.src = url.href;
        }
      }, 200)
    );
  }
}
