import { join, resolve } from "path";

import { ESBuildMinifyPlugin } from "esbuild-loader";
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import TerserPlugin from "terser-webpack-plugin";
import { DefinePlugin } from "webpack";
import type { Configuration } from "webpack";

import { config } from "./package.json";

const prod = process.env.NODE_ENV === "production";

function compact<T>(arr: (T | undefined)[]): T[] {
  return arr.filter((e) => e !== undefined && typeof e !== "undefined") as T[];
}

function prodOr<P = any, D = P>(pVal: P, dVal: D): P | D {
  return prod ? pVal : dVal;
}

function ifProd<T>(obj: T): T | undefined {
  return prodOr(obj, undefined);
}

const relToRoot = (...args: string[]) => resolve(__dirname, ...args);
const relToSrc = (...args: string[]) => relToRoot("src", ...args);

const [hashFunction, hashDigestLength] = ["md5", 28];

const outPath = relToRoot("static", "dist");

const mode = prodOr("production", "development");
const publicPath = "/static/dist/";
const contenthash = prodOr(".[contenthash]", "");

const configuration: Configuration = {
  entry: config.entry,
  output: {
    filename: `[name]${contenthash}.js`,
    path: outPath,
    hashFunction,
    hashDigestLength,
    publicPath,
  },
  devtool: prodOr("source-map", "cheap-module-source-map"),
  mode,
  plugins: [
    new MiniCssExtractPlugin({
      filename: `style.[name]${contenthash}.css`,
      chunkFilename: `[name]${contenthash}.css`,
    }),
    new HtmlWebpackPlugin({
      filename: relToRoot("holdmypics", "core", "templates", "base-out.html"),
      minify: false,
      inject: false,
      meta: {},
      cache: false,
    }),
    new DefinePlugin({
      PRODUCTION: JSON.stringify(prod),
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(ts)$/,
        include: [relToSrc("ts")],
        exclude: [/node_modules/],
        use: [
          {
            loader: require.resolve("esbuild-loader"),
            options: {
              loader: "ts",
              target: "es2015",
              tsconfigRaw: require("./src/tsconfig.json"),
            },
          },
          /*{
            loader: require.resolve("babel-loader"),
            options: {
              cacheDirectory: false,
              exclude: /node_modules/,
              presets: compact([
                ifProd([
                  "@babel/preset-env",
                  {
                    corejs: { version: "3.13", proposals: true },
                    debug: process.env.BABEL_DEBUG !== undefined,
                    useBuiltIns: "usage",
                    targets: { esmodules: true },
                    exclude: ["@babel/plugin-transform-template-literals"],
                    bugfixes: true,
                  },
                ]),
                ["@babel/typescript", { onlyRemoveTypeImports: true }],
              ]),
              plugins: ["@babel/proposal-object-rest-spread"],
              parserOpts: {
                strictMode: true,
              },
            },
          },*/
        ],
      },
      {
        test: /\.(scss)$/,
        include: [relToSrc("scss")],
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: require.resolve("css-loader"),
            options: { importLoaders: 2, modules: false },
          },
          { loader: require.resolve("postcss-loader") },
          {
            loader: require.resolve("sass-loader"),
            options: { sassOptions: { outputStyle: "expanded" } },
          },
        ],
      },
      {
        test: /\.(css)$/,
        include: [relToSrc("css")],
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: require.resolve("css-loader"),
            options: { importLoaders: 2, modules: false },
          },
          { loader: require.resolve("postcss-loader") },
        ],
      },
      {
        test: /\.(woff2?)$/,
        include: [relToSrc("scss")],
        type: "asset/resource",
        generator: {
          filename: join("fonts", `[name]${contenthash}[ext]`),
        },
      },
    ],
  },
  optimization: {
    minimizer: compact([
      ifProd(
        new ESBuildMinifyPlugin({ target: "es2015" })
        // new TerserPlugin({
        //   terserOptions: {
        //     compress: {
        //       drop_console: false,
        //       drop_debugger: true,
        //       global_defs: {
        //         PRODUCTION: true,
        //       },
        //     },
        //   },
        // })
      ),
    ]),
    splitChunks: {
      automaticNameDelimiter: "~",
    },
  },
  resolve: {
    extensions: [".js", ".ts"],
    symlinks: false,
  },
  node: false,
  stats: {
    modules: false,
    children: false,
    excludeAssets: [/fonts[\\/]spectral-/, /\.map$/, /\.LICENSE\.txt$/],
    publicPath: true,
    cachedAssets: true,
    hash: true,
  },
  recordsPath: relToSrc(`webpack-records-${prodOr("prod", "dev")}.json`),
  cache: {
    type: "filesystem",
    buildDependencies: {
      config: [__filename, relToRoot("postcss.config.js")],
    },
  },
};

export default configuration;
