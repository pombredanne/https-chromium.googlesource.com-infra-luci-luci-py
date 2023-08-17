// Copyright 2023 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { PrpcService } from "./common";

const QUERY_START_TS = 4;
const QUERY_ALL = 10;

/**
 * Service to communicate with swarming.v2.Bots prpc service.
 */
export class BotsService extends PrpcService {
  get service() {
    return "swarming.v2.Bots";
  }

  /**
   * Calls the GetBot route.
   *
   *  @param {String} bot_id - identifier of the bot to retrieve.
   *
   *  @returns {Object} object with information about the bot in question.
   */
  getBot(botId) {
    return this._call("GetBot", { bot_id: botId });
  }

  /**
   * Calls the ListBotTasks route
   *
   *  @param {String} bot_id - identifier of the bot to retrieve.
   *  @param {String} cursor - cursor retrieved from previous request to ListBotTasks.
   *
   *  @returns {Object} object containing both items and cursor fields. `items` contains a list of tasks associated with the Bot and `cursor` is a db cursor from the previous request.
   */
  getTasks(botId, cursor) {
    const request = {
      sort: QUERY_START_TS,
      state: QUERY_ALL,
      bot_id: botId,
      cursor: cursor,
      limit: 30,
      include_performance_stats: true,
    };
    return this._call("ListBotTasks", request);
  }

  /**
   * Terminates a bot given a botId.
   *
   * @param {String} botId - identifier of bot to terminate.
   *
   * @returns {Object} with the shape {taskId: "some_task_id"} if the termination operation was initiated without error
   *
   **/
  terminate(botId) {
    const request = {
      bot_id: botId,
    };
    return this._call("TerminateBot", request);
  }

  /**
   * Requests a list of BotEvents for a given botId
   *
   * @param {String} botId - identifier of bot from which to retrieve events.
   * @param {String} cursor - cursor from previous request.
   *
   * @returns {Object} with shape {cursor: "some_cursor", items: [... list of bot events ...]}
   **/
  events(botId, cursor) {
    const request = {
      limit: 50,
      bot_id: botId,
      cursor: cursor,
    };
    return this._call("ListBotEvents", request);
  }

  /**
   * Deletes bot with the given botId
   *
   * @param {String} botId - identifier of bot to delete.
   *
   * @returns {Object} with shape { deleted: bool } where deleted is true if the bot was actually deleted.
   **/
  delete(botId) {
    return this._call("DeleteBot", { bot_id: botId });
  }

  count(dimensions) {
    return this._call("CountBots", { dimensions });
  }
}
