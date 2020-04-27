import * as path from "path";
import process from "process";

import autoprefixer from "autoprefixer";
import webpack, { CliConfigOptions } from "webpack";
import * as Clean from "clean-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import HtmlWebpackPlugin from "html-webpack-plugin";

import OptimizeCSSPlugin = require("optimize-css-assets-webpack-plugin");
import TerserPlugin = require("terser-webpack-plugin");

import * as pkg from "./package.json";

const prod = process.env.NODE_ENV === "production";

function compact<T>(arr: (T | undefined)[]): T[] {
  return arr.filter((e) => e !== undefined && typeof e !== "undefined") as T[];
}

function prodOr<P = any, D = any>(pVal: P, dVal: D): P | D {
  return prod ? pVal : dVal;
}

function ifProd<T>(obj: T): T | undefined {
  return prodOr(obj, undefined);
}

const cleanExts = ["css", "js", "svg", "txt", "map"];
const doClean = cleanExts.map((ext) => `**/*.${ext}`);
const dontClean = ["!**/fonts", "!**/fonts/**/*", "!img", "!img/**/*"];
const cleanPatterns = doClean.concat(dontClean);
const cleanOpts: Clean.Options = {
  verbose: false,
  dry: false,
  cleanOnceBeforeBuildPatterns: cleanPatterns,
  cleanStaleWebpackAssets: false,
};

const relToRoot = (...args: string[]) => path.resolve(__dirname, ...args);
const relToNode = (...args: string[]) => relToRoot("node_modules", ...args);
const relToSrc = (...args: string[]) => relToRoot("src", ...args);

const hashFn = prodOr("sha256", "md4");
const hashlength = prodOr(28, 10);
const fontHash = `${hashFn}:hash:hex:${hashlength}`;
const fontName = `[path][name].[${fontHash}].[ext]`;

const rootDir = relToRoot("holdmypics");
const outPath = path.join(__dirname, "static", "dist");

const templatesDir = path.join(rootDir, "core", "templates");

const publicPath = "/static/dist/";

const configureBabel = () => {
  return {
    loader: "babel-loader",
    options: {
      cacheDirectory: prodOr(false, path.resolve(__dirname, ".cache", "babel")),
      cacheCompression: true,
      exclude: /node_modules/,
      presets: [
        [
          "@babel/preset-env",
          {
            corejs: { version: 3, proposals: true },
            debug: false,
            useBuiltIns: "usage",
            targets: { esmodules: true },
          },
        ],
        "@babel/typescript",
      ],
      plugins: [
        ["@babel/plugin-transform-runtime", { useESModules: true }],
        "@babel/proposal-object-rest-spread",
      ],
      parserOpts: {
        strictMode: true,
      },
    },
  };
};

const configureStyles = () => {
  return [
    MiniCssExtractPlugin.loader,
    {
      loader: "css-loader",
      options: {
        importLoaders: 2,
        sourceMap: prod,
        modules: false,
      },
    },
    {
      loader: "postcss-loader",
      options: {
        sourceMap: true,
        plugins: [autoprefixer({ flexbox: "no-2009" })],
      },
    },
    {
      loader: "sass-loader",
      options: {
        implementation: require("sass"),
        sassOptions: {
          outputStyle: prodOr("compressed", "expanded"),
        },
      },
    },
  ];
};

const config: webpack.Configuration = {
  entry: pkg.entry,
  output: {
    filename: `[name].[contenthash:${hashlength}].js`,
    path: outPath,
    hashFunction: hashFn,
    hashDigestLength: 64,
    publicPath,
    pathinfo: !prod,
  },
  devtool: prodOr("source-map", "cheap-module-eval-source-map"),
  mode: prodOr("production", "development"),
  plugins: [
    new Clean.CleanWebpackPlugin(cleanOpts),
    new MiniCssExtractPlugin({
      filename: `style.[name].[contenthash:${hashlength}].css`,
      chunkFilename: `[name].[contenthash:${hashlength}].css`,
    }),
    new HtmlWebpackPlugin({
      filename: path.join(templatesDir, "base-out.html"),
      minify: false,
      inject: false,
      meta: {},
      cache: false,
    }),
    new webpack.DefinePlugin({
      PRODUCTION: JSON.stringify(prod),
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(ts)$/,
        use: [configureBabel()],
        include: [relToSrc("ts")],
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: "html-loader",
            options: {
              attributes: false,
            },
          },
        ],
      },
      {
        test: /\.(s?css)$/,
        include: [relToSrc("scss")],
        use: configureStyles(),
      },
      {
        test: /\.(woff|woff2)$/,
        include: [relToSrc("scss")],
        use: [
          {
            loader: "file-loader",
            options: {
              context: "src/scss/theme",
              name: fontName,
              esModule: false,
            },
          },
        ],
      },
    ],
  },
  optimization: {
    minimizer: compact([
      ifProd(
        new TerserPlugin({
          cache: true,
          parallel: true,
          sourceMap: true,
          terserOptions: {
            parse: {
              html5_comments: false,
              shebang: false,
            },
            compress: {
              drop_console: true,
              drop_debugger: true,
              ecma: 2016,
              passes: 2,
              global_defs: {
                PRODUCTION: true,
              },
            },
            output: {
              comments: false,
              ecma: 2016,
              indent_level: 2,
            },
          },
        })
      ),
      ifProd(
        new OptimizeCSSPlugin({
          cssProcessor: require("cssnano"),
          cssProcessorOptions: { preset: ["default"], map: true },
          canPrint: false,
        })
      ),
    ]),
    splitChunks: {
      automaticNameDelimiter: "-",
      cacheGroups: {
        corejs_es: {
          test: /node_modules[\\/]core-js[\\/]modules[\\/]es/,
          name: "core-js-es",
          minChunks: 1,
          chunks: "all",
          priority: 20,
        },
        corejs_web: {
          test: /node_modules[\\/]core-js[\\/]modules[\\/]web/,
          name: "core-js-web",
          minChunks: 1,
          chunks: "all",
        },
        corejs_internal: {
          test: /node_modules[\\/]core-js[\\/]internals[\\/]/,
          name: "core-js-internal",
          minChunks: 1,
          chunks: "all",
        },
      },
    },
  },
  resolve: {
    extensions: [".js", ".ts"],
    symlinks: false,
    alias: {
      Feather: relToNode("feather-icons", "dist", "icons"),
    },
  },
  node: false,
  stats: {
    modules: false,
    children: false,
    excludeAssets: [
      /fonts[\\/]spectral-/,
      /\.map$/,
      /\.woff$/,
      /\.LICENSE\.txt$/,
    ],
    publicPath: true,
    cachedAssets: true,
  },
};

type Env = string | Record<string, boolean | number | string>;
export default config;
// export default function (env: Env, args: CliConfigOptions) {  }
