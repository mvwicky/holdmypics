const { join } = require("path");

const autoprefixer = require("autoprefixer");

const plugins = [autoprefixer({ flexbox: "no-2009" })];

if (process.env.NODE_ENV === "production") {
  const purgeCSS = require("@fullhuman/postcss-purgecss");
  const reporter = require("postcss-reporter");
  const csso = require("postcss-csso");

  const content = ["jinja", "html"].map((ext) =>
    join(".", "holdmypics", "**", `*.${ext}`)
  );
  const safelist = {
    deep: [/tippy/],
  };
  plugins.push(
    purgeCSS({ content, safelist, rejected: true }),
    csso({}),
    reporter({ filter: (msg) => /purgecss/.test(msg.plugin) })
  );
}

module.exports = { plugins };
