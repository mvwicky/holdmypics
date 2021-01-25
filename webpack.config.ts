import { join, resolve } from "path";
import process from "process";

import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import TerserPlugin = require("terser-webpack-plugin");
import webpack from "webpack";
import type { Configuration } from "webpack";

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

const relToRoot = (...args: string[]) => resolve(__dirname, ...args);
const relToNode = (...args: string[]) => relToRoot("node_modules", ...args);
const relToSrc = (...args: string[]) => relToRoot("src", ...args);

const [hashFn, hashlength] = ["md5", 28];

const rootDir = relToRoot("holdmypics");
const outPath = join(__dirname, "static", "dist");

const templatesDir = join(rootDir, "core", "templates");

const mode = prodOr("production", "development");
const publicPath = "/static/dist/";
const contenthash = prodOr(".[contenthash]", "");

const config: Configuration = {
  entry: pkg.entry,
  output: {
    filename: `[name]${contenthash}.js`,
    path: outPath,
    hashFunction: hashFn,
    hashDigestLength: hashlength,
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
      filename: join(templatesDir, "base-out.html"),
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
        use: [
          {
            loader: require.resolve("babel-loader"),
            options: {
              cacheDirectory: relToNode(".cache", "babel", mode),
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
        ],
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
        use: [
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
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: false,
              drop_debugger: true,
              ecma: 2018,
              global_defs: {
                PRODUCTION: true,
              },
            },
          },
        })
      ),
    ]),
    splitChunks: {
      automaticNameDelimiter: "~",
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
  cache: {
    type: "filesystem",
    buildDependencies: {
      config: [__filename],
    },
  },
};

export default config;
