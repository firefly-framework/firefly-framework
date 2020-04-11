/*
 * Copyright (c) 2019 JD Williams
 *
 * This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
 * redistribute it and/or modify it under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 3 of the License, or (at your option) any later version.
 *
 * Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
 * implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License for more details. You should have received a copy of the GNU Lesser General Public
 * License along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * You should have received a copy of the GNU General Public License along with Firefly. If not, see
 * <http://www.gnu.org/licenses/>.
 */


const path = require('path');
const webpack = require('webpack');
const HtmlWebPackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const DuplicatePackageCheckerPlugin = require("duplicate-package-checker-webpack-plugin");
const WebpackWatchPlugin = require('webpack-watch-files-plugin').default;
const DotEnv = require('dotenv-webpack');

module.exports = (env) => {
  return {
    entry: {
      firefly: [
        "./__target__/src.firefly_web.app.js",
        "./src/firefly_web/styles.scss"
      ]
    },
    output: {
      filename: "[name].js",
      library: "[name]",
      // libraryTarget: "umd",
      // globalObject: "this",
    },
    devServer: {
      overlay: true,
      hot: true,
    },
    resolve: {
      extensions: ['.js'],
      modules: [
        path.resolve(__dirname, 'node_modules'),
        'node_modules',
      ],
    },
    optimization: {
      minimize: false
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader"
          }
        },
        {
          test: /\.(svg)$/,
          use: {
            loader: "svg-inline-loader",
          }
        },
        // {
        //   test: /\.py$/,
        //   loader: "transcrypt-loader",
        //   options: {
        //     command: '. venv/bin/activate && python3 -m transcrypt',
        //     arguments: [
        //       '--nomin',
        //       '--map',
        //       '--fcall',
        //       '--verbose',
        //     ]
        //   }
        // },
        {
          test: /\.(sa|sc|c)ss$/,
          use: [
            {
              loader: MiniCssExtractPlugin.loader,
              options: {
                hmr: true,
                reloadAll: true,
              }
            },
            "css-loader",
            {
              loader: "postcss-loader",
              options: {
                ident: "postcss",
                plugins: [
                  require("tailwindcss"),
                  require("autoprefixer"),
                ],
              },
            },
            {
              loader: "sass-loader",
              options: {
                sassOptions: (loaderContext) => {
                  const output = require('child_process').execSync(
                      './venv/bin/pip show firefly-framework',
                  );
                  const fireflyPath = /Location:\s([^\n]+)/.exec(output)[1];

                  return {
                    includePaths: [`${fireflyPath}/firefly/presentation/web/styles`],
                  };
                },
              },
            },
          ],
        },
      ]
    },
    plugins: [
      new DotEnv({
        path: `./.env.${env}`,
        expand: true,
      }),
      new MiniCssExtractPlugin({
        filename: "[name].css",
        chunkFilename: "[name].css"
      }),
      new HtmlWebPackPlugin({
        filename: "index.html",
        template: path.resolve(__dirname, 'src/firefly_web/index.html'),
        excludeChunks: ["serviceWorker"]
      }),
      new DuplicatePackageCheckerPlugin(),
      new WebpackWatchPlugin({
        files: [
          './__target__/*.js'
        ]
      }),
      new webpack.HotModuleReplacementPlugin(),
    ]
  };
};
