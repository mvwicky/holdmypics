const postcssImport = require("postcss-import");
const tailwindCSS = require("tailwindcss");

const plugins = [postcssImport, tailwindCSS];

if (process.env.NODE_ENV === "production") {
  const autoprefixer = require("autoprefixer");
  plugins.push(autoprefixer({ flexbox: "no-2009" }));
}

module.exports = { plugins };
