import { join, resolve } from "path";

import { ESBuildMinifyPlugin } from "esbuild-loader";
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
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

const rel = {
  toRoot: (...args: string[]) => resolve(__dirname, ...args),
  toSrc: (...args: string[]) => resolve(__dirname, "src", ...args),
} as const;

const outPath = rel.toRoot("static", "dist");

const mode = prodOr("production", "development");
const publicPath = "/static/dist/";
const contenthash = prodOr(".[contenthash]", "");

const entry = Object.fromEntries(
  Object.entries(config.entry).map(([name, e]) => [name, resolve(e)])
);
const templateDir = rel.toRoot("holdmypics", "core", "templates");

const configuration: Configuration = {
  entry,
  output: {
    filename: `[name]${contenthash}.js`,
    chunkFilename: `chunks/[name]${contenthash}.js`,
    path: outPath,
    hashFunction: "xxhash64",
    publicPath,
  },
  devtool: prodOr("source-map", "source-map"),
  mode,
  plugins: [
    new MiniCssExtractPlugin({
      filename: join("css", `style.[name]${contenthash}.css`),
      chunkFilename: join("css", `[name]${contenthash}.css`),
    }) as any,
    new HtmlWebpackPlugin({
      filename: join(templateDir, "base-out.html"),
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
        test: /\.ts$/,
        include: [rel.toSrc("ts")],
        exclude: [/node_modules/],
        use: [
          {
            loader: require.resolve("esbuild-loader"),
            options: {
              loader: "ts",
              target: "es2015",
              tsconfigRaw: require("./src/ts/tsconfig.json"),
            },
          },
        ],
      },
      {
        test: /\.css$/,
        include: [rel.toSrc("css")],
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: require.resolve("css-loader"),
            options: { importLoaders: 1, modules: false, import: false },
          },
          { loader: require.resolve("postcss-loader") },
        ],
      },
      {
        test: /\.woff2?$/,
        include: [rel.toSrc("css")],
        type: "asset/resource",
        generator: { filename: `fonts/[name]${contenthash}[ext]` },
      },
    ],
  },
  optimization: {
    minimizer: compact([
      ifProd(new ESBuildMinifyPlugin({ target: "es2015", css: true })),
    ]),
    splitChunks: { automaticNameDelimiter: "~" },
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
  recordsPath: rel.toSrc(`webpack-records-${prodOr("prod", "dev")}.json`),
  cache: {
    type: "filesystem",
    buildDependencies: {
      config: [
        __filename,
        rel.toRoot("postcss.config.js"),
        rel.toRoot("tailwind.config.js"),
      ],
    },
  },
  watchOptions: {
    ignored: [
      "**/*.py",
      "**/node_modules",
      outPath,
      templateDir,
      rel.toSrc("webpack-records-*.json"),
      rel.toRoot("holdmypics"),
    ],
  },
};

export default configuration;
