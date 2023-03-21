// Copyright 2023 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { PrpcClient } from '@chopsui/prpc-client';

class PrpcService {
  /**
   * @param {string} accessToken - bearer token to use to authenticate requests.
   * @param {AbortController} signal - abort controller provided by caller if
   *  we wish to abort request
   * @param {Object} opts - @chopui/prpc-client PrpcOptions, additional options.
   */
  constructor(accessToken, signal=null, opts={}) {
    let prpcOpts = {
      ...opts, accessToken: undefined
    }
    // If we are running a live_demo, this will be set so we must override
    // the PrpcClients host function.
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

/**
 * Service to communicate with swarming.v2.Bots prpc service.
 */
export class BotsService extends PrpcService {
  static Service = "swarming.v2.Bots"

  constructor(authToken, signal) {
    super(authToken, signal);
  }

  get service() {
    return "swarming.v2.Bots"
  }

  /**
   * Calls the GetBot route.
   *
   *  @param {String} bot_id - Identifier of the bot to retrieve.
   *
   *  @returns {Object} object with information about the bot in question.
   */
  getBot(botId) {
    return this._call('GetBot', { bot_id: botId });
  }
}

