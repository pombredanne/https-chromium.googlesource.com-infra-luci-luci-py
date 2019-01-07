// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { html } from 'lit-html'
import { botPageLink, compareWithFixedOrder, humanDuration, sanitizeAndHumanizeTime,
         taskPageLink } from '../util'

const BLACKLIST_DIMENSIONS = ['quarantined', 'error'];

export function appendPossibleColumns(possibleColumns, data) {
  // Use name as a sentinal value
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

/** column returns the display-ready value for a column (aka key)
 *  from a task. It requires the entire state (ele) for potentially complicated
 *  data lookups (and also visibility of the 'verbose' setting).
 *  A custom version can be specified in colMap, with the default being
 *  the attribute of task in col or 'none'.
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
  if (col.endsWith('-tag')) {
    col = col.substring(0, col.length - 4);
  }
  let c = colMap[col];
  if (c) {
    return c(task, ele);
  }
  let tags = task.tagMap[col];
  if (tags) {
    if (ele._verbose) {
      return tags.join(' | ');
    }
    return tags[0];
  }
  return task[col] || 'none';
}

export function getColHeader(col) {
  if (col.endsWith('-tag')) {
    return `${col.substring(0, col.length - 4)} (tag)`;
  }
  return colHeaderMap[col] || col;
}

// This puts the times in a aesthetically pleasing order, roughly in
// the order everything happened.
const specialColOrder = ['name', 'created_ts', 'pending_time',
    'started_ts', 'duration', 'completed_ts', 'abandoned_ts', 'modified_ts'];
const compareColumns = compareWithFixedOrder(specialColOrder);

/** sortColumns sorts the bot-list columns in mostly alphabetical order. Some
  columns (id, task) go first to maintain with behavior from previous
  versions.
  @param cols Array<String> The columns
*/
export function sortColumns(cols) {
  cols.sort(compareColumns);
}

/** sortPossibleColumns sorts the columns in the column selector. It puts the
 *  selected ones on top in the order they are displayed and the rest below
 *  in alphabetical order.
 */
export function sortPossibleColumns(keys, selectedCols) {
  let selected = {};
  for (let c of selectedCols) {
    selected[c] = true;
  }

  keys.sort((a, b) => {
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

const TASK_TIMES = ['abandoned_ts', 'completed_ts', 'created_ts', 'modified_ts',
                    'started_ts'];

/** processTasks processes the array of tasks from the server and returns it.
 *  The primary goal is to get the data ready for display.
 *
 * @param cols Array<Object> The raw tasks objects.
 */
export function processTasks(arr, existingTags) {
  if (!arr) {
    return [];
  }
  let now = new Date();
  let knownTags = {};

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
      existingTags[key] = true;
    }
    task.tagMap = tagMap;

    if (!task.costs_usd || !Array.isArray(task.costs_usd)) {
      task.costs_usd = '‑‑';
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

      task.pending_time = null;
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
  // TODO(kjlubick) old version has special handling of tags -
  // turns foo-tag into foo (tag)
}

const extraKeys = ['name', 'state', 'costs_usd', 'deduped_from', 'duration', 'pending_time',
  'server_versions', 'bot', ...TASK_TIMES];

// Given a time attribute like 'abandoned_ts', humanTime returns a function
// that returns the human-friendly version of that attribute. The human
// friendly time was created in task-list-data.
function humanTime(attr) {
  return (task) => {
    return task['human_' + attr];
  }
}

const colMap = {
  abandoned_ts: humanTime('abandoned_ts'),
  bot: function(task) {
    let id = task.bot_id;
    if (id) {
      return html`<a target=_blank
                   rel=noopener
                   href=${botPageLink(id)}>${id}</a>`;
    }
    return '--';
  },
  completed_ts: humanTime('completed_ts'),
  costs_usd: function(task) {
    return task.costs_usd;
  },
  created_ts: humanTime('created_ts'),
  duration: humanTime('duration'),
  modified_ts: humanTime('modified_ts'),
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
  pending_time: humanTime('pending_time'),
  source_revision: function(task) {
    let r = task.source_revision;
    return r.substring(0, 8);
  },
  started_ts: humanTime('started_ts'),
  state: function(task) {
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