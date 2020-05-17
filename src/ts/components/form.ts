import { elemIsTag } from "../helpers/elem-is-tag";

const checks = [elemIsTag.bind(null, "input"), elemIsTag.bind(null, "select")];

function isInput(e: Element): e is FormInput {
  return checks.some((f) => f(e));
}

function isCheckbox(inp: HTMLInputElement): boolean {
  return inp.type === "checkbox";
}

export class ImageForm {
  private readonly form: HTMLFormElement;
  private elements: FormInput[] = [];

  constructor(form: HTMLFormElement) {
    this.form = form;
    this.elements = Array.from(form.elements).filter(isInput);
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
}
