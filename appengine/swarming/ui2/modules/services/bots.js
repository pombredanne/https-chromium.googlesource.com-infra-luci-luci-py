// Copyright 2023 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { PrpcClient } from '@chopsui/prpc-client';

class PrpcService {
  constructor(accessToken, signal=null, opts={}) {
    let prpcOpts = {
      ...opts, accessToken: undefined
    }
    if (window.DEV_HOST) {
      prpcOpts.host = window.DEV_HOST
    }
    this._token = accessToken
    if (signal) {
      let fetchFn = (url, opts) => {
        opts.signal = signal
        return fetch(url, opts)
      }
      prpcOpts.fetchImpl = fetchFn
    }
    this._client = new PrpcClient(prpcOpts);
  }

  get service() {
    throw "Subclasses must define service"
  }

  _call(method, request) {
    const additionalHeaders = {
      authorization: this._token,
    }
    return this._client.call(this.service, method, request, additionalHeaders);
  }
}

export class BotsService extends PrpcService {
  static Service = "swarming.v2.Bots"

  constructor(authToken, signal) {
    super(authToken, signal);
  }

  get service() {
    return "swarming.v2.Bots"
  }

  getBot(botId) {
    return this._call('GetBot', { bot_id: botId });
  }
}
