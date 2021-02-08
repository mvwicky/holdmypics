const { join } = require("path");

const autoprefixer = require("autoprefixer");

const plugins = [autoprefixer({ flexbox: "no-2009" })];

if (process.env.NODE_ENV === "production") {
  const purgeCSS = require("@fullhuman/postcss-purgecss");
  const csso = require("postcss-csso");

  const content = ["jinja", "html"].map((ext) =>
    join(".", "holdmypics", "**", `*.${ext}`)
  );
  plugins.push(purgeCSS({ content, rejected: true }), csso({}));
  if (process.env.SHOW_PURGED_CLASSES !== undefined) {
    const reporter = require("postcss-reporter");
    plugins.push(reporter({ filter: (msg) => /purgecss/.test(msg.plugin) }));
  }
}

module.exports = { plugins };
