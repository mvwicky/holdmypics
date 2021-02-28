module.exports = {
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ["tsconfig.json"],
  },
  env: { node: false, browser: true },
  globals: { PRODUCTION: "readonly" },
};
