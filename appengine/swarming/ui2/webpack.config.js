// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

const { commonBuilder } = require('pulito');
const path = require('path');

module.exports = commonBuilder(__dirname);

module.exports.output.publicPath='/newres/'

module.exports.module.rules.push({
  test: /.js$/,
  use: [
    {
      loader: path.resolve('html-template-minifier/loader.js'),
      options: {
        alpha: 'beta',
      },
    },
  ]
})