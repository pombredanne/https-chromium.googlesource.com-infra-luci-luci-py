// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

const commonBuilder = require('pulito');
const path = require('path');

module.exports = (env, argv) => {
  let config = commonBuilder(env, argv, __dirname);
  // Make all CSS/JS files appear at the /newres location.
  config.output.publicPath='/newres/';
  config.module.rules.push({
    test: /.js$/,
    use: 'html-template-minifier-webpack',
  });

  // TODO(kjlubick): remove after https://github.com/google/pulito/pull/3 lands
  config.plugins.forEach((p) => {
    if ('HtmlWebpackPlugin' === p.constructor.name && p.options) {
      p.options.minify = {
        caseSensitive: true,
        collapseBooleanAttributes: true,
        collapseWhitespace: true,
        minifyCSS: true,
        minifyJS: true,
        minifyURLS: true,
        removeOptionalTags: true,
        removeRedundantAttributes: true,
        removeScriptTypeAttributes: true,
        removeStyleLinkTypeAttributes: true,
      };
    }
  });
  return config;
}
