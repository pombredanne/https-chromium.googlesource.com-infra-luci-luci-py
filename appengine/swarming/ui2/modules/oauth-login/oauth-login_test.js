// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import 'modules/oauth-login';

describe('oauth-login', function() {
  // A reusable HTML element in which we create our element under test.
  const container = document.createElement('div');
  document.body.appendChild(container);

  afterEach(function() {
    container.innerHTML = '';
  });

  // ===============TESTS START====================================

  describe('testing-offline true', function() {
    // calls the test callback with one element 'ele', a created <oauth-login>.
    function createElement(test) {
      return window.customElements.whenDefined('oauth-login').then(() => {
        container.innerHTML = `<oauth-login testing_offline=true></oauth-login>`;
        expect(container.firstElementChild).toBeTruthy();
        expect(container.firstElementChild.testing_offline).toBeTruthy();
        test(container.firstElementChild);
      });
    }

    it('starts off logged out', function(done) {
      createElement((ele) => {
        expect(ele.auth_header).toBe('');
        done();
      });
    });

    it('triggers a log-in custom event on login', function(done) {
      createElement((ele) => {
        ele.addEventListener('log-in', (e) => {
          e.stopPropagation();
          expect(e.detail).toBeDefined();
          expect(e.detail.auth_header).toContain('Bearer ');
          done();
        });
        ele._logIn();
      });
    });

    it('has auth_header set after log-in', function(done) {
      createElement((ele) => {
        ele._logIn();
        expect(ele.auth_header).toContain('Bearer ');
        done();
      });
    });
  }); // end describe('testing-offline true')

  describe('testing-offline false', function() {
    // calls the test callback with one element 'ele', a created <oauth-login>.
    function createElement(test) {
      return window.customElements.whenDefined('oauth-login').then(() => {
        container.innerHTML = `<oauth-login></oauth-login>`;
        expect(container.firstElementChild).toBeTruthy();
        expect(container.firstElementChild.testing_offline).toBeFalsy();
        test(container.firstElementChild);
      });
    }

    it('starts off logged out', function(done) {
      createElement((ele) => {
        expect(ele.auth_header).toBe('');
        done();
      });
    });
  }); // end describe('testing-offline false')
});
