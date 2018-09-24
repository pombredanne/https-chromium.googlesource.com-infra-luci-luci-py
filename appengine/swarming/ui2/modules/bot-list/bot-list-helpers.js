
import { diffDate } from 'common-sk/modules/human'
import { html, render } from 'lit-html/lib/lit-extended'
import naturalSort from 'javascript-natural-sort/naturalSort'

export function aggregateTemps(temps) {
  if (!temps) {
    return {};
  }
  let zones = [];
  let avg = 0;
  for (let k in temps) {
    zones.push(k +': '+temps[k]);
    avg += (+temps[k]);
  }
  avg = avg / zones.length
  if (avg) {
    avg = avg.toFixed(1);
  } else {
    avg = 'unknown';
  }
  return {
    average: avg,
    zones: zones.join(' | ') || 'unknown',
  }
}

/* attribute() looks first in dimension and then in state for the
 * specified attribute. This will always return an array. If there is
 * no matching attribute, ['unknown'] will be returned.
 */
export function attribute(bot, attr, none) {
  none = none || 'UNKNOWN';
  return fromDimension(bot, attr) || fromState(bot, attr) || [none];
}

export function botLink(botId) {
  return `/bot?id=${botId}`;
}

export function column(col, bot, ele) {
  if (!bot) {
    console.warn('falsey bot passed into column');
    return '';
  }
  let c = colMap[col];
  if (c) {
    return c(bot, ele);
  }
  return longestOrAll(attribute(bot, col, 'none'), ele._verbose);
}

export function devices(bot) {
  return bot.state.devices || [];
}

export function fromDimension(bot, dim) {
  if (!bot || !bot.dimensions || !dim) {
    return null;
  }
  for (let i = 0; i < bot.dimensions.length; i++) {
    if (bot.dimensions[i].key === dim) {
      return bot.dimensions[i].value;
    }
  }
  return null;
}

export function fromState(bot, attr) {
  if (!bot || !bot.state || !bot.state[attr]) {
    return null;
  }
  let state = bot.state[attr];
  if (Array.isArray(state)) {
    return state;
  }
  return [state];
}

export function longestOrAll(arr, verbose) {
  if (verbose) {
    return arr.join(' | ');
  }
  let most = '';
  for(let i = 0; i < arr.length; i++) {
    if (arr[i] && arr[i].length > most.length) {
      most = arr[i];
    }
  }
  return most;
}

export function makeFilter(key, value) {
  return `${key}:${value}`;
}

/* Do any pre-processing of the bot list here. */
export function processBots(arr) {
  if (!arr) {
    return [];
  }
  arr.forEach((bot) => {
    bot.state = (bot.state && JSON.parse(bot.state)) || {};
    // get the disks in an easier to deal with format, sorted by size.
    let disks = bot.state.disks || {};
    let keys = Object.keys(disks);
    if (!keys.length) {
      bot.disks = [{'id': 'unknown', 'mb': 0}];
    } else {
      bot.disks = [];
      for (let i = 0; i < keys.length; i++) {
        bot.disks.push({'id':keys[i], 'mb':disks[keys[i]].free_mb});
      }
      // Sort these so the biggest disk comes first.
      bot.disks.sort(function(a, b) {
        return b.mb - a.mb;
      });
    }

    // Make sure every bot has a state.temp object and precompute
    // average and list of temps by zone if applicable.
    bot.state.temp = aggregateTemps(bot.state.temp);

    let devices = [];
    let d = (bot && bot.state && bot.state.devices) || {};
    // state.devices is like {Serial:Object}, so we need to keep the serial
    for (let key in d) {
      let o = d[key];
      o.serial = key;
      o.okay = (o.state === 'available');
      // It is easier to assume all devices on a bot are of the same type
      // than to pick through the (incomplete) device state and find it.
      // Bots that are quarantined because they have no devices
      // still have devices in their state (the last known device attached)
      // but don't have the device_type dimension. In that case, we punt
      // on device type.
      let types = fromDimension(bot, 'device_type') || ['unknown'];
      o.device_type = types[0];
      o.temp = aggregateTemps(o.temp);
      devices.push(o);
    }
    // For determinism, sort by device id
    devices.sort((a,b) => {
      // Don't use natural sort because that can confusingly put
      // 89ABCDEF012 before 3456789ABC
      if (a.serial < b.serial) {
        return -1;
      } else if (a.serial > b.serial) {
        return 1;
      }
      return 0;
    });
    bot.state.devices = devices;
  });
  // TODO(kjlubick): do more here and write some tests for it.

  return arr;
}

export function processDimensions(arr) {
  if (!arr) {
    return [];
  }
  let dims = [];
  arr.forEach(function(d){
    if (blacklistDimensions.indexOf(d.key) === -1) {
      dims.push(d.key);
    }
  });
  // Make sure 'id' is in there, but not duplicated (see blacklistDimensions)
  dims.push('id');
  dims.sort();
  return dims;
}

export function processPrimaryMap(dimensions){
  // pMap will have a list of columns to available values (primary key
  // to secondary values). This includes bot dimensions, but also
  // includes state like disk_space, quarantined, busy, etc.
  dimensions = dimensions || [];

  var pMap = {};
  dimensions.forEach(function(d){
    if (blacklistDimensions.indexOf(d.key) >= 0) {
      return;
    }
    // TODO(kjlubick)
    if (true || swarming.alias.DIMENSIONS_WITH_ALIASES.indexOf(d.key) === -1) {
      // value is an array of all seen values for the dimension d.key
      pMap[d.key] = d.value;
    } else {
      var aliased = [];
      d.value.forEach(function(value){
        aliased.push(swarming.alias.apply(value, d.key));
      });
      pMap[d.key] = aliased;
    }
  });

  // Add some options that might not show up.
  pMap['android_devices'] && pMap['android_devices'].push('0');
  pMap['device_os'] && pMap['device_os'].push('none');
  pMap['device_type'] && pMap['device_type'].push('none');

  pMap['id'] = [];

  // Create custom filter options
  pMap['disk_space'] = [];
  pMap['task'] = ['busy', 'idle'];
  pMap['status'] = ['alive', 'dead', 'quarantined', 'maintenance'];
  pMap['is_mp_bot'] = ['true', 'false'];

  // No need to sort any of this, bot-filters sorts secondary items
  // automatically, especially when the user types a query.
  return pMap;
}

export function taskLink(taskId, disableCanonicalID) {
  if (!taskId) {
    return undefined;
  }
  if (!disableCanonicalID) {
    // task abcefgh0 is the 'canonical' task id. The first try has the id
    // abcefgh1. If there is a second (transparent retry), it will be
    // abcefgh2.  We almost always want to link to the canonical one,
    // because the milo output (if any) will only be generated for
    // abcefgh0, not abcefgh1 or abcefgh2.
    taskId = taskId.substring(0, taskId.length - 1) + '0';
  }
  return `/task?id=${taskId}`;
}

const blacklistDimensions = ['quarantined', 'error', 'id'];

export const extraKeys = ['disk_space', 'uptime', 'running_time', 'task',
'status', 'version', 'external_ip', 'internal_ip', 'mp_lease_id', 'mp_lease_expires',
'last_seen', 'first_seen', 'battery_level', 'battery_voltage', 'battery_temperature',
'battery_status', 'battery_health', 'bot_temperature', 'device_temperature', 'is_mp_bot'];

export const colHeaderMap = {
  'id': 'Bot Id',
  'mp_lease_id': 'Machine Provider Lease Id',
  'task': 'Current Task',
  'android_devices': 'Android Devices',
  'battery_health': 'Battery Health',
  'battery_level': 'Battery Level (%)',
  'battery_status': 'Battery Status',
  'battery_temperature': 'Battery Temp (°C)',
  'battery_voltage': 'Battery Voltage (mV)',
  'bot_temperature': 'Bot Temp (°C)',
  'cores': 'Cores',
  'cpu': 'CPU',
  'device': 'Non-android Device',
  'device_os': 'Device OS',
  'device_temperature': 'Device Temp (°C)',
  'device_type': 'Device Type',
  'disk_space': 'Free Space (MB)',
  'external_ip': 'External IP',
  'first_seen': 'First Seen',
  'gpu': 'GPU',
  'internal_ip': 'Internal or Local IP',
  'last_seen': 'Last Seen',
  'mp_lease_expires': 'Machine Provider Lease Expires',
  'os': 'OS',
  'pool': 'Pool',
  'running_time': 'Swarming Uptime',
  'status': 'Status',
  'uptime': 'Bot Uptime',
  'xcode_version': 'XCode Version',
};

export const specialSortMap = {
  id: (dir, botA, botB) => dir * naturalSort(botA.bot_id, botB.bot_id),
};

const colMap = {
  id: (bot, ele) => html`<a target=_blank
                            rel=noopener
                            href=${botLink(bot.bot_id)}>${bot.bot_id}</a>`,
  status: (bot, ele) => {
    if (bot.is_dead) {
      return `Dead. Last seen ${diffDate(bot.last_seen_ts)} ago`;
    }
    if (bot.quarantined) {
      let msg = fromState(bot, 'quarantined');
      if (msg) {
        msg = msg[0];
      };
      // Sometimes, the quarantined message is actually in 'error'.  This
      // happens when the bot code has thrown an exception.
      if (!msg || msg === 'true' || msg === true) {
        msg = attribute(bot, 'error')[0];
      }
      // Other times, the bot has reported it is quarantined by setting the
      // dimension 'quarantined' to be something.
      if (msg === 'UNKNOWN') {
        msg = fromDimension(bot, 'quarantined') || 'UNKNOWN';
      }
      let errs = [];
      // Show all the errors that are active on devices to make it more
      // clear if this is a transient error (e.g. device is too hot)
      // or if it is requires human interaction (e.g. device is unauthorized)
      devices(bot).forEach(function(d){
        if (d.state !== 'available') {
          errs.push(d.state);
        }
      });
      if (errs.length) {
        msg += ` [${errs.join(',')}]`;
      }
      return `Quarantined: ${msg}`;
    }
    if (bot.maintenance_msg) {
      return `Maintenance: ${bot.maintenance_msg}`;
    }
    return 'Alive';
  },
  task: (bot, ele) => {
    if (!bot.task_id) {
      return 'idle';
    }
    return html`<a target=_blank
                   rel=noopener
                   title=${bot.task_name}
                   href=${taskLink(bot.task_id)}>${bot.task_id}</a>`;
  },
};
