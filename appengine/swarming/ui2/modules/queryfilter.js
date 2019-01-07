// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.
import { applyAlias } from './alias'

/** filterPossibleColumns shows only those columns that match the given query.
 *  This means, if there is a part of the query in the column (ignoring case).
 */
export function filterPossibleColumns(allCols, query) {
  if (!query) {
    return allCols;
  }
  return allCols.filter((c) => {
    return matchPartCaseInsensitive(c, query);
  });
}

/** filterPossibleKeys shows only those keys that match the given query.
 *  This means, if there is a part of the key in the column (ignoring case),
 *  or if any value associated to the key (via keyMap) matches.
 */
export function filterPossibleKeys(allKeys, keyMap, query) {
  if (!query) {
    return allKeys;
  }
  query = query.trim();
  if (query.indexOf(':') === -1) {
    return allKeys.filter((k) => {
      if (matchPartCaseInsensitive(k, query)) {
        return true;
      }
      let values = keyMap[k] || [];
      for (let value of values) {
        value = applyAlias(value, k);
        if (matchPartCaseInsensitive(value, query)) {
          return true;
        }
      }
      return false;
    });
  }
  // partial queries should only show the key that exactly matches
  query = query.split(':')[0];
  return allKeys.filter((k) => {
    if (k === query) {
      return true;
    }
    return false;
  });
}

/** filterPossibleValues shows some values associated with the given query.
 * If the user has typed in a query, show all secondary elements if
 * their primary element matches.  If it doesn't match the primary
 * element, only show those secondary elements that do.
 */
export function filterPossibleValues(allValues, selectedKey, query) {
  // only look for first index, since value can have colons (e.g. gpu)
  query = query.trim();
  let colonIdx = query.indexOf(':');
  if (colonIdx !== -1) {
    query = query.substring(colonIdx+1);
  }
  if (!query || matchPartCaseInsensitive(selectedKey, query)) {
    return allValues;
  }
  return allValues.filter((v) => {
    v = applyAlias(v, selectedKey);
    if (matchPartCaseInsensitive(v, query)) {
      return true;
    }
    return false;
  });
}
/** matchPartCaseInsensitive returns true or false if str matches any
 *of a space separated list of queries,
 */
function matchPartCaseInsensitive(str, queries) {
  if (!queries) {
    return true;
  }
  if (!str) {
    return false
  }
  queries = queries.trim().toLocaleLowerCase();
  str = str.toLocaleLowerCase();
  let xq = queries.split(' ');
  for (let query of xq) {
    let idx = str.indexOf(query);
    if (idx !== -1) {
      return true;
    }
  }
  return false;
};