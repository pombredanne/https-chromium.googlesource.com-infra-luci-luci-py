// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import './index.js'

//import botListData from './bot-list_data.js'
import { data_s10 } from './test_data'

// Can't use import fetch-mock because the library isn't quite set up
// correctly for it, and we get strange errors about 'this' not being defined.
const fetchMock = require('fetch-mock');

// uncomment to stress test with 2560 items
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);
// data_s10.items.push(...data_s10.items);

function requireLogin(logged_in, delay=100) {
  return function(url, opts){
    if (opts && opts.headers && opts.headers.authorization) {
      return new Promise((resolve) => {
        setTimeout(resolve, delay);
      }).then(() => {
        return {
          status: 200,
          body: JSON.stringify(logged_in),
          headers: {'Content-Type':'application/json'},
        };
      });
    } else {
      console.log('Not logged in?');
      return new Promise((resolve) => {
        setTimeout(resolve, delay);
      }).then(() => {
        return {
          status: 403,
          body: 'Try logging in',
          headers: {'Content-Type':'text/plain'},
        };
      });
    }
  };
}

fetchMock.get('/_ah/api/swarming/v1/bots/list', requireLogin(data_s10));

// Everything else
fetchMock.catch(404);

// autologin
document.querySelector('oauth-login')._logIn();