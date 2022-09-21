// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

const CopyWebpackPlugin = require('copy-webpack-plugin');
const commonBuilder = require('./webpack_config/webpack.common');

module.exports = (env, argv) => {
  const config = commonBuilder(env, argv, __dirname);
  // Make all CSS/JS files appear at the /newres location.
  config.output.publicPath='/newres/';
  if (argv.mode === 'production') {
    config.module.rules.push({
      test: /.js$/,
      use: 'html-template-minifier-webpack',
    });
  }
  config.plugins.push(
      new CopyWebpackPlugin({
        patterns: [
          'node_modules/@webcomponents/custom-elements/custom-elements.min.js',
        ]}),
  );

  return config;
};
