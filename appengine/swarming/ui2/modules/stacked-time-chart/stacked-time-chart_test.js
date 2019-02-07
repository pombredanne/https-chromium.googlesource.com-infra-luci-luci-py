// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import 'modules/stacked-time-chart'

fdescribe('stacked-time-chart', function() {

  const { $, $$ } = require('common-sk/modules/dom');
  const { customMatchers } = require('modules/test_util');

  beforeEach(function() {
    jasmine.addMatchers(customMatchers);
  });

  const container = document.createElement('div');
  document.body.appendChild(container);

  afterEach(function() {
    container.innerHTML = '';
  });

  // calls the test callback with one element 'ele', a created <stacked-time-chart>.
  function createElement(test) {
    return window.customElements.whenDefined('stacked-time-chart').then(() => {
      container.innerHTML = `<stacked-time-chart></stacked-time-chart>`;
      expect(container.firstElementChild).toBeTruthy();
      test(container.firstElementChild);
    });
  }

  it('has a test', function(done) {
    createElement((ele) => {
      expect(ele).toBeTruthy();
      done();
    });
  });
});
