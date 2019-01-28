// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import 'modules/task-page'

describe('task-page', function() {
  // Instead of using import, we use require. Otherwise,
  // the concatenation trick we do doesn't play well with webpack, which would
  // leak dependencies (e.g. bot-list's 'column' function to task-list) and
  // try to import things multiple times.
  const { $$ } = require('common-sk/modules/dom');

  // A reusable HTML element in which we create our element under test.
  const container = document.createElement('div');
  document.body.appendChild(container);

  afterEach(function() {
    container.innerHTML = '';
  });

//===============TESTS START====================================

  // calls the test callback with one element 'ele', a created <task-page>.
  function createElement(test) {
    return window.customElements.whenDefined('task-page').then(() => {
      container.innerHTML = `<task-page></task-page>`;
      expect(container.firstElementChild).toBeTruthy();
      test(container.firstElementChild);
    });
  }


});