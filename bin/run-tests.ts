import * as path from "path";

import cypress from "cypress";

const root = path.dirname(__dirname);
const spec = path.join(root, "cypress", "integration", "index.spec.ts");

cypress.run({ record: false, spec });
