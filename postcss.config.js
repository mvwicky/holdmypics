const autoprefixer = require("autoprefixer");
// require("tailwindcss"),
const plugins = [autoprefixer({ flexbox: "no-2009" })];
if (process.env.NODE_ENV === "production") {
  plugins.push(require("cssnano"));
}

module.exports = { plugins, map: true };
