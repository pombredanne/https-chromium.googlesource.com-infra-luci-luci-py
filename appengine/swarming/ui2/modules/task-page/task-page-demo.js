// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.
import './index.js'

import { taskResult, taskRequest } from './test_data'
import { requireLogin, mockAuthdAppGETs } from '../test_util'

(function(){
// Can't use import fetch-mock because the library isn't quite set up
// correctly for it, and we get strange errors about 'this' not being defined.
const fetchMock = require('fetch-mock');

// uncomment to stress test with 5120 items
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);
// bots_10.items.push(...bots_10.items);

mockAuthdAppGETs(fetchMock, {
  cancel_task: true,
});

fetchMock.get('glob:/_ah/api/swarming/v1/task/*/request',
              requireLogin(taskRequest, 100));

fetchMock.get('glob:/_ah/api/swarming/v1/task/*/result?include_performance_stats=true',
              requireLogin(taskResult, 200));

// Everything else
fetchMock.catch(404);

// autologin for ease of testing locally - comment this out if using the real flow.
document.querySelector('oauth-login')._logIn();
})();