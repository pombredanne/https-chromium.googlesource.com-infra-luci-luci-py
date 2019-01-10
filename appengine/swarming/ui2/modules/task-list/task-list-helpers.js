// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { applyAlias } from '../alias'
import { html } from 'lit-html'
import naturalSort from 'javascript-natural-sort/naturalSort'
import { botPageLink, compareWithFixedOrder, humanDuration, sanitizeAndHumanizeTime,
         taskPageLink } from '../util'

const BLACKLIST_DIMENSIONS = ['quarantined', 'error'];
const EMPTY_VAL = '--';

/** appendPossibleColumns takes the given data and derives columns
 *  that could be displayed. There are two possible data sources:
 *    - the list of dimensions seen on bots from the server
 *    - a map of tags seen on the lists so far
 *  There is also a list of 'hard coded' columns that should be
 *  viable (see possibleColumns) which is added if it does not exist.
 *
 * @param {Object} possibleColumns - Existing set (i.e. String->bool) of
 *        columns so far. New data will be appended to this.
 * @param {Object|Array} data - one of two options listed above.
 */
export function appendPossibleColumns(possibleColumns, data) {
  // Use name as a sentinel value
  if (!possibleColumns['name']) {
    for (let col of extraKeys) {
      possibleColumns[col] = true;
    }
  }
  if (Array.isArray(data)) {
    // we have a list of dimensions, which are {key: String, value: Array}
    for (let dim of data) {
      if (BLACKLIST_DIMENSIONS.indexOf(dim.key) === -1) {
        possibleColumns[dim.key + '-tag'] = true;
      }
    }
  } else {
    // data is a map of tag -> values
    for (let tag in data) {
      possibleColumns[tag + '-tag'] = true;
    }
  }
}

/** appendPrimaryMap builds up a map of primary keys (e.g. left column) based
 *  on dimensions and other interesting options (e.g. device-related things).
 *  The primary keys map to the values they could be filtered by.
 */
export function appendPrimaryMap(primaryMap, data) {
  // Use name as a sentinel value
  if (!primaryMap['name']) {
    primaryMap['state'] = ['PENDING', 'RUNNING', 'PENDING_RUNNING', 'COMPLETED',
            'COMPLETED_SUCCESS', 'COMPLETED_FAILURE', 'EXPIRED', 'TIMED_OUT',
            'BOT_DIED', 'CANCELED', 'DEDUPED', 'ALL', 'NO_RESOURCE'];
  }
  if (Array.isArray(data)) {
    // we have a list of dimensions, which are {key: String, value: Array}
    for (let dim of data) {
      if (BLACKLIST_DIMENSIONS.indexOf(dim.key) === -1) {
        let existing = primaryMap[dim.key + '-tag'];
        for (let value of dim.value) {
          existing = _insertUnique(existing, value);
        }
        primaryMap[dim.key + '-tag'] = existing;
      }
    }
  } else {
    // data is a map of tag -> values
    for (let tag in data) {
      let existing = primaryMap[tag + '-tag'];
        for (let value of data[tag]) {
          existing = _insertUnique(existing, value);
        }
        primaryMap[tag + '-tag'] = existing;
    }
  }
}

/** column returns the display-ready value for a column (aka key)
 *  from a task. It requires the entire state (ele) for potentially complicated
 *  data lookups (and also visibility of the 'verbose' setting).
 *  A custom version can be specified in colMap, with the default being
 *  the attribute of task in col or '--'.
 *
 * @param {string} col - The 'key' of the data to pull.
 * @param {Object} task - The task from which to extract data.
 * @param {Object} ele - The entire task-list object, for context.
 *
 * @returns {String} - The requested column, ready for display.
 */
export function column(col, task, ele) {
  if (!task) {
    console.warn('falsey task passed into column');
    return '';
  }
  let c = colMap[col];
  if (c) {
    return c(task, ele);
  }

  col = stripTag(col);
  let tags = task.tagMap[col];
  if (tags) {
    tags = tags.map((t) => applyAlias(t, col));
    if (ele._verbose) {
      return tags.join(' | ');
    }
    return tags[0];
  }
  return task[col] || EMPTY_VAL;
}

// A list of special rules for filters. In practice, this is anything
// that is not a dimension, since the API only supports filtering by
// dimensions and these values.
// This should not be directly used by task-list, but is exported for
// testing.
export const specialFilters = {
  state: function(task, s) {
    let state = task.state;
    if (s === state || s === 'ALL') {
      return true;
    }
    if (s === 'PENDING_RUNNING') {
      return state === 'PENDING' || state === 'RUNNING';
    }
    let failure = task.failure;
    if (s === 'COMPLETED_SUCCESS') {
      return state === 'COMPLETED' && !failure;
    }
    if (s === 'COMPLETED_FAILURE') {
      return state === 'COMPLETED' && failure;
    }
    let tryNum = task.try_number;
    if (s === 'DEDUPED') {
      return state === 'COMPLETED' && tryNum === '0';
    }
  }
};


/** Filters the tasks like they would be filtered from the server
 * @param {Array<String>} filters - e.g. ['alpha:beta']
 * @param {Array<Object>} bots: the bot objects to filter.
 *
 * @returns {Array<Object>} the tasks that match the filters.
*/
export function filterTasks(filters, tasks) {
  let parsedFilters = [];
  // Preprocess the filters
  for (let filterString of filters) {
    let idx = filterString.indexOf(':');
    let key = filterString.slice(0, idx);
    let value = filterString.slice(idx + 1);
    parsedFilters.push([key, value]);
  }
  // apply the filters in an AND way, that is, it must
  // match all the filters
  return tasks.filter((task) => {
    let matches = true;
    for (let filter of parsedFilters) {
      let [key, value] = filter;
      if (specialFilters[key]) {
        matches &= specialFilters[key](task, value);
      } else {
        key = stripTag(key);
        // it's a tag,  which is *not* aliased, so we can just
        // do an exact match (reminder, aliasing only happens in column)
        matches &= ((task.tagMap[key] || []).indexOf(value) !== -1);
      }
    }
    return matches;
  });
  return tasks;
}

/** getColHeader returns the human-readable header for a given column.
 */
export function getColHeader(col) {
  if (col && col.endsWith('-tag')) {
    return `${stripTag(col)} (tag)`;
  }
  return colHeaderMap[col] || col;
}

function _insertUnique(arr, value) {
  // TODO(kjlubick): this could be tuned with binary search.
  if (!arr || !arr.length) {
    return [value];
  }
  for (let i = 0; i < arr.length; i++) {
    // Do not add duplicates
    if (value === arr[i]) {
      return arr;
    }
    // We have found where value should go in sorted order.
    if (value < arr[i]) {
      arr.splice(i, 0, value);
      return arr;
    }
  }
  // value must be bigger than all elements, append to end.
  arr.push(value);
  return arr;
}

/** processTasks processes the array of tasks from the server and returns it.
 *  The primary goal is to get the data ready for display.
 *  This function builds onto the set of tags seen overall, which is used
 *  for filtering.
 *
 * @param {Array<Object>} arr - The raw tasks objects.
 * @param {Object} existingTags - a map (String->Array<String>) of tags
 *      to values. The values array should be sorted with no duplicates.
 */
export function processTasks(arr, existingTags) {
  if (!arr) {
    return [];
  }
  let now = new Date();

  for (let task of arr) {
    let tagMap = {};
    task.tags = task.tags || [];
    for (let tag of task.tags) {
      let split = tag.split(':', 1)
      let key = split[0];
      let rest = tag.substring(key.length + 1);
      // tags are free-form, and could be duplicated
      if (!tagMap[key]) {
        tagMap[key] = [rest];
      } else {
        tagMap[key].push(rest);
      }
      existingTags[key] = _insertUnique(existingTags[key], rest);
    }
    task.tagMap = tagMap;

    if (!task.costs_usd || !Array.isArray(task.costs_usd)) {
      task.costs_usd = EMPTY_VAL;
    } else {
      task.costs_usd.forEach(function(c, idx) {
        task.costs_usd[idx] = '$' + c.toFixed(4);
        if (task.state === 'RUNNING' && task.started_ts) {
          task.costs_usd[idx] = task.costs_usd[idx] + '*';
        }
      });
    }

    for (let time of TASK_TIMES) {
      sanitizeAndHumanizeTime(task, time);

      // Running tasks have no duration set, so we can figure it out.
      if (!task.duration && task.state === 'RUNNING' && task.started_ts) {
        task.duration = (now - task.started_ts) / 1000;
      }
      // Make the duration human readable
      task.human_duration = humanDuration(task.duration);
      if (task.state === 'RUNNING' && task.started_ts) {
        task.human_duration = task.human_duration + '*';
      }

      // Deduplicated tasks usually have tasks that ended before they were
      // created, so we need to account for that.
      let et = task.started_ts || task.abandoned_ts || new Date();
      let deduped = (task.created_ts && et < task.created_ts);

      task.pending_time = undefined;
      if (!deduped && task.created_ts) {
        task.pending_time = (et - task.created_ts) / 1000;
      }
      task.human_pending_time = humanDuration(task.pending_time);
      if (!deduped && task.created_ts && !task.started_ts && !task.abandoned_ts) {
        task.human_pending_time = task.human_pending_time + '*';
      }
    };
  }
  return arr;
}

// This puts the times in a aesthetically pleasing order, roughly in
// the order everything happened.
const specialColOrder = ['name', 'created_ts', 'pending_time',
    'started_ts', 'duration', 'completed_ts', 'abandoned_ts', 'modified_ts'];
const compareColumns = compareWithFixedOrder(specialColOrder);

/** sortColumns sorts the bot-list columns in mostly alphabetical order. Some
 *  columns (name) go first or are sorted in a fixed order (timestamp ones)
 *  to aid reading.
 *  @param {Array<String>} cols - The columns
*/
export function sortColumns(cols) {
  cols.sort(compareColumns);
}

/** sortPossibleColumns sorts the columns in the column selector. It puts the
 *  selected ones on top in the order they are displayed and the rest below
 *  in alphabetical order.
 *
 * @param {Array<String>} columns - The columns to sort. They will be sorted
 *          in place.
 * @param {Array<String>} selectedCols - The currently selected columns.
 */
export function sortPossibleColumns(columns, selectedCols) {
  let selected = {};
  for (let c of selectedCols) {
    selected[c] = true;
  }

  columns.sort((a, b) => {
      // Show selected columns above non selected columns
      let selA = selected[a];
      let selB = selected[b];
      if (selA && !selB) {
        return -1;
      }
      if (selB && !selA) {
        return 1;
      }
      if (selA && selB) {
        // Both keys are selected, thus we put them in display order.
        return compareColumns(a, b);
      }
      // neither column was selected, fallback to alphabetical sorting.
      return a.localeCompare(b);
  });
}

/** stripTag removes the '-tag' suffix from a string, if there is one, and
 *  returns what remains.
 */
export function stripTag(s) {
  if (s && s.endsWith('-tag')) {
    return s.substring(0, s.length - 4);
  }
  return s;
}

/** taskClass returns the CSS class for the given task, based on the state
 *  of said task.
 */
export function taskClass(task) {
  let state = column('state', task);
   if (state === 'CANCELED' || state === 'TIMED_OUT' || state === 'EXPIRED' || state === 'NO_RESOURCE') {
      return 'exception';
    }
    if (state === 'BOT_DIED') {
      return 'bot_died';
    }
    if (state === 'COMPLETED (FAILURE)') {
      return 'failed_task';
    }
    if (state === 'RUNNING' || state === 'PENDING') {
      return 'pending_task';
    }
    return '';
}


/** colHeaderMap maps keys to their human readable name.*/
const colHeaderMap = {
  'abandoned_ts': 'Abandoned On',
  'completed_ts': 'Completed On',
  'bot': 'Bot Assigned',
  'costs_usd': 'Cost (USD)',
  'created_ts': 'Created On',
  'duration': 'Duration',
  'modified_ts': 'Last Modified',
  'started_ts': 'Started Working On',
  'user': 'Requesting User',
  'pending_time': 'Time Spent Pending',
}

const TASK_TIMES = ['abandoned_ts', 'completed_ts', 'created_ts', 'modified_ts',
                    'started_ts'];

const extraKeys = ['name', 'state', 'costs_usd', 'deduped_from', 'duration', 'pending_time',
  'server_versions', 'bot', ...TASK_TIMES];

const colMap = {
  abandoned_ts: (task) => task.human_abandoned_ts,
  bot: (task) => {
    let id = task.bot_id;
    if (id) {
      return html`<a target=_blank
                   rel=noopener
                   href=${botPageLink(id)}>${id}</a>`;
    }
    return EMPTY_VAL;
  },
  completed_ts: (task) => task.human_completed_ts,
  costs_usd: function(task) {
    return task.costs_usd;
  },
  created_ts: (task) => task.human_created_ts,
  duration: (task) => task.human_duration,
  modified_ts: (task) => task.human_modified_ts,
  name: (task, ele) => {
    let name = task.name;
    if (!ele._verbose && task.name.length > 70) {
      name = name.slice(0, 67) + '...';
    }
    return html`<a target=_blank
                   rel=noopener
                   title=${task.name}
                   href=${taskPageLink(task.task_id)}>${name}</a>`;
  },
  pending_time: (task) => task.human_pending_time,
  source_revision: (task) => {
    let r = task.source_revision;
    return r.substring(0, 8);
  },
  started_ts: (task) => task.human_started_ts,
  state: (task) => {
    let state = task.state;
    if (state === 'COMPLETED') {
      if (task.failure) {
        return 'COMPLETED (FAILURE)';
      }
      if (task.try_number === '0') {
        return 'COMPLETED (DEDUPED)';
      }
      return 'COMPLETED (SUCCESS)';
    }
    return state;
  },
}

/** specialSortMap maps keys to their special sort rules, encapsulated in a
 *  function. The function takes in the current sort direction (1 for ascending)
 *  and -1 for descending and both bots and should return a number a la compare.
 */
export const specialSortMap = {
  abandoned_ts: sortableTime('abandoned_ts'),
  bot: (dir, taskA, taskB) => dir * naturalSort(taskA.bot_id || 'z', taskB.bot_id || 'z'),
  completed_ts: sortableTime('completed_ts'),
  created_ts: sortableTime('created_ts'),
  duration: sortableDuration('duration'),
  modified_ts: sortableTime('modified_ts'),
  name: (dir, taskA, taskB) => dir * naturalSort(taskA.name, taskB.name),
  pending_time: sortableDuration('pending_time'),
  started_ts: sortableTime('started_ts'),
};

// Given a time attribute like 'abandoned_ts', sortableTime returns a function
// that compares the tasks based on the attribute.  This is used for sorting.
function sortableTime(attr) {
  // sort times based on the string they come with, formatted like
  // '2016-08-16T13:12:40.606300' which sorts correctly.  Locale time
  // (used in the columns), does not.
  return (dir, a, b) => {
    let aCol = a[attr] || '9999';
    let bCol = b[attr] || '9999';

    return dir * (aCol - bCol);
  }
}

// like sortableTime but for durations, making a careful distinction
// between 0 and undefined.
function sortableDuration(attr) {
  return (dir, a, b) => {
    let aCol = a[attr] !== undefined ? a[attr] : 1e12;
    let bCol = b[attr] !== undefined ? b[attr] : 1e12;

    return dir * (aCol - bCol);
  }
}