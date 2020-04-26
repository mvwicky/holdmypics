import * as path from "path";

import cypress from "cypress";

const spec = path.join(
  path.dirname(__dirname),
  "cypress",
  "integration",
  "index.spec.ts"
);

cypress.run({
  record: false,
  spec,
});
