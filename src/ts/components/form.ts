import { elemIsTag } from "../helpers/elem-is-tag";
import type { EndpointPathArgs, FormInput } from "../types";

const checks = [elemIsTag.bind(null, "input"), elemIsTag.bind(null, "select")];

function isInput(e: Element): e is FormInput {
  return checks.some((f) => f(e));
}

function isCheckbox(inp: HTMLInputElement): boolean {
  return inp.type === "checkbox";
}

export class ImageForm {
  private readonly elements: FormInput[];

  constructor(private readonly form: HTMLFormElement) {
    this.form = form;
    this.elements = [...form.elements].filter(isInput);
  }

  gatherPath(): Partial<EndpointPathArgs> {
    return {};
  }

  gatherQuery(): [string, string][] {
    const queryInputs = this.elements.filter((elem) =>
      elem.classList.contains("query")
    );
    const args: [string, string][] = [];
    queryInputs.forEach((inp) => {
      if (inp.checkValidity() && !inp.disabled) {
        if (elemIsTag("select", inp)) {
          args.push([inp.id, inp.value]);
        } else if (isCheckbox(inp)) {
          args.push([inp.id, inp.checked ? "on" : ""]);
        } else {
          args.push([inp.id, inp.value && inp.value.trim()]);
        }
      }
    });
    return args;
  }

  createSearchParams(): URLSearchParams {
    const params = new URLSearchParams(this.gatherQuery());
    return params;
  }

  createURL(): URL {
    const { action } = this.form;
    const url = new URL(action, self.location.href);
    url.search = this.createSearchParams().toString();
    return url;
  }
}
