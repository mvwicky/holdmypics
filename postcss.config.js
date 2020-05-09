/* eslint-env node */

const autoprefixer = require("autoprefixer");
const plugins = [autoprefixer({ flexbox: "no-2009" })];
if (process.env.NODE_ENV === "production") {
  plugins.push(
    require("@fullhuman/postcss-purgecss")({
      defaultExtractor: (content) => content.match(/[\w-/.:]+(?<!:)/g) || [],
      content: ["./holdmypics/**/*.jinja", "./holdmypics/**/*.html"],
    })
  );
}

module.exports = { plugins, map: true };
