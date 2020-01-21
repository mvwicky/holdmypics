import * as path from "path";
import process from "process";

import webpack from "webpack";
import {
  CleanWebpackPlugin,
  Options as CleanOptions
} from "clean-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import HtmlWebpackPlugin from "html-webpack-plugin";

import OptimizeCSSPlugin = require("optimize-css-assets-webpack-plugin");
import TerserPlugin = require("terser-webpack-plugin");

import * as pkg from "./package.json";

const prod = process.env.NODE_ENV === "production";

function compact<T>(arr: (T | undefined)[]): T[] {
  return arr.filter(e => e !== undefined && typeof e !== "undefined") as T[];
}

function prodOr<P = any, D = any>(pVal: P, dVal: D): P | D {
  return prod ? pVal : dVal;
}

function ifProd<T>(obj: T): T | undefined {
  return prodOr(obj, undefined);
}

const cleanOpts: CleanOptions = {
  verbose: false,
  dry: false,
  cleanOnceBeforeBuildPatterns: [
    "**/*",
    "!fonts",
    "!fonts/**/*",
    "!img",
    "!img/**/*"
  ]
};

const hashFn = prodOr("sha256", "md5");
const hashlength = prodOr(32, 10);
const fontHash = `${hashFn}:hash:hex:${hashlength}`;
const fontName = `[name].[${fontHash}].[ext]`;

const srcDir = path.resolve(__dirname, "src");
const dummyDir = path.resolve(__dirname, "dummy_flask");
// const outPath = path.resolve(__dirname, "dist");
const outPath = path.join(dummyDir, "static", "dist");

const templatesDir = path.join(dummyDir, "core", "templates");

const publicPath = "/static/dist/";

const config: webpack.Configuration = {
  entry: pkg.entry,
  output: {
    filename: `[name].[contenthash:${hashlength}].js`,
    path: outPath,
    hashFunction: "sha256",
    hashDigestLength: 64,
    publicPath
  },
  devtool: prodOr("source-map", "cheap-module-eval-source-map"),
  mode: prodOr("production", "development"),
  plugins: [
    new CleanWebpackPlugin(cleanOpts),
    new MiniCssExtractPlugin({
      filename: `style.[contenthash:${hashlength}].css`
    }),
    new HtmlWebpackPlugin({
      filename: path.join(templatesDir, "base-out.html"),
      template: path.join(srcDir, "template.html"),
      minify: false,
      inject: true
    })
  ],
  module: {
    rules: [
      {
        test: /\.(ts)$/,
        use: [
          {
            loader: "babel-loader",
            options: {
              cacheDirectory: prodOr(false, path.resolve(__dirname, ".cache")),
              exclude: /node_modules/,
              presets: [
                [
                  "@babel/preset-env",
                  {
                    corejs: { version: 3, proposals: true },
                    modules: false,
                    debug: false,
                    useBuiltIns: "usage"
                  }
                ],
                "@babel/typescript"
              ],
              plugins: [
                "@babel/plugin-proposal-optional-chaining",
                "@babel/proposal-object-rest-spread"
              ],
              parserOpts: {
                strictMode: true
              }
            }
          }
        ],
        include: path.join(srcDir)
      },
      {
        test: /\.(s?css)$/,
        use: compact([
          {
            loader: MiniCssExtractPlugin.loader
          },
          {
            loader: "css-loader",
            options: {
              importLoaders: prodOr(2, 1),
              sourceMap: prod
            }
          },
          ifProd({
            loader: "postcss-loader",
            options: {
              sourceMap: true,
              plugins: () => {
                return [require("autoprefixer")];
              }
            }
          }),
          {
            loader: "sass-loader",
            options: {
              implementation: require("sass"),
              sassOptions: {
                outputStyle: "expanded"
              }
            }
          }
        ])
      }
    ]
  },
  optimization: {
    minimizer: compact([
      ifProd(
        new TerserPlugin({
          cache: true,
          parallel: true,
          sourceMap: true
        })
      ),
      ifProd(
        new OptimizeCSSPlugin({
          cssProcessor: require("cssnano"),
          cssProcessorOptions: { preset: ["default"], map: true },
          canPrint: false
        })
      )
    ])
  },
  resolve: {
    extensions: [".js"],
    symlinks: false
  },
  node: false,
  stats: {
    modules: false,
    children: false,
    excludeAssets: [/^fonts\//]
  }
};

export default config;
