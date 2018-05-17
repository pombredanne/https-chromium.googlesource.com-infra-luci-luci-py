import './index.js'

// Can't use import fetch-mock because the library isn't quite set up
// correctly for it, and we get strange errors about 'this' not being defined.
const fetchMock = require('fetch-mock')

const details = {
  server_version: '1234-deadbeef',
  bot_version: 'abcdoeraymeyouandme',
};

const respond = function(url, opts){
  // if (!request.requestHeaders.authorization) {
  //   console.log('You must be logged in (check your Oauth?)');
  //   request.respond(403, {}, 'You must be logged in (check your Oauth?)');
  //   return;
  // }
  console.log('User authenticated :) ', url, opts);
  return {
    status: 200,
    body: JSON.stringify(details),
    headers: {'Content-Type':'application/json'},
  }
}

fetchMock.get('/api/swarming/v1/server/details', respond);


const permissions = {
  get_bootstrap_token: true
}

fetchMock.get('/api/swarming/v1/server/permissions', JSON.stringify(permissions));

const token = {
  bootstrap_token: '8675309JennyDontChangeYourNumber8675309'
}

fetchMock.get('/api/swarming/v1/server/token', JSON.stringify(token));