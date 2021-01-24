import * as path from "path";
import process from "process";

import * as Clean from "clean-webpack-plugin";
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import OptimizeCSSPlugin = require("optimize-css-assets-webpack-plugin");
import TerserPlugin = require("terser-webpack-plugin");
import webpack from "webpack";

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
const doClean: string[] = cleanExts.map((ext) => `**/*.${ext}`);
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

function configureBabel(): webpack.RuleSetUseItem[] {
  return [
    {
      loader: require.resolve("babel-loader"),
      options: {
        cacheDirectory: relToNode(".cache", "babel", prodOr("prod", "dev")),
        cacheCompression: true,
        exclude: /node_modules/,
        presets: [
          [
            "@babel/preset-env",
            {
              corejs: { version: "3", proposals: true },
              debug: false,
              useBuiltIns: "usage",
              targets: { esmodules: true },
              exclude: ["@babel/plugin-transform-template-literals"],
              bugfixes: true,
            },
          ],
          "@babel/typescript",
        ],
        plugins: [
          "@babel/proposal-class-properties",
          "@babel/plugin-transform-classes",
          "@babel/proposal-object-rest-spread",
        ],
        parserOpts: {
          strictMode: true,
        },
      },
    },
  ];
}

function configureStyles(): webpack.RuleSetUseItem[] {
  return [
    MiniCssExtractPlugin.loader,
    {
      loader: require.resolve("css-loader"),
      options: {
        importLoaders: 2,
        sourceMap: prod,
        modules: false,
      },
    },
    { loader: require.resolve("postcss-loader") },
    { loader: require.resolve("sass-loader") },
  ];
}

function configurePlugins(): webpack.Plugin[] {
  return [
    new Clean.CleanWebpackPlugin(cleanOpts),
    new MiniCssExtractPlugin({
      filename: `style.[name].[contenthash].css`,
      chunkFilename: `[name].[contenthash].css`,
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
    new webpack.HashedModuleIdsPlugin({ hashDigestLength: 4 }),
  ];
}

const config: webpack.Configuration = {
  entry: pkg.entry,
  output: {
    filename: `[name].[contenthash].js`,
    path: outPath,
    hashFunction: hashFn,
    hashDigestLength: hashlength,
    publicPath,
    pathinfo: !prod,
  },
  devtool: prodOr("source-map", "cheap-module-eval-source-map"),
  mode: prodOr("production", "development"),
  plugins: configurePlugins(),
  module: {
    rules: [
      {
        test: /\.(ts)$/,
        use: configureBabel(),
        include: [relToSrc("ts")],
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: require.resolve("html-loader"),
            options: {
              attributes: false,
              minimize: false,
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
        test: /\.(woff2?)$/,
        include: [relToSrc("scss")],
        use: [
          {
            loader: require.resolve("file-loader"),
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
              drop_console: false,
              drop_debugger: true,
              ecma: 2018,
              passes: 1,
              global_defs: {
                PRODUCTION: true,
              },
              keep_fnames: true,
            },
            output: {
              comments: false,
              ecma: 2016,
              indent_level: 2,
            },
            mangle: {
              keep_fnames: true,
            },
          },
        })
      ),
      ifProd(
        new OptimizeCSSPlugin({
          cssProcessor: require("cssnano"),
          cssProcessorOptions: { preset: ["default"], map: true },
        })
      ),
    ]),
    splitChunks: {
      automaticNameDelimiter: "-",
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
    excludeAssets: [/fonts[\\/]spectral-/, /\.map$/, /\.LICENSE\.txt$/],
    publicPath: true,
    cachedAssets: true,
  },
  recordsPath: relToSrc("webpack-records.json"),
};

type Env = string | Record<string, boolean | number | string>;
export default config;
// export default function (env: Env, args: CliConfigOptions) {  }
