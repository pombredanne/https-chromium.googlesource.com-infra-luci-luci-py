// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { html } from 'lit-html'

export function attribute(task, col, def) {
  return ['todo '+def];
}

export function column(col, task, ele) {
  if (!task) {
    console.warn('falsey task passed into column');
    return '';
  }
  let c = colMap[col];
  if (c) {
    return c(task, ele);
  }
  let values = attribute(task, col, 'none');
   // tasks tend to have only one of a given thing, unlike
   // bots, which broadcast several of the same dimension.
  return values[0];
}

export function processTasks(arr) {
  if (!arr) {
    return [];
  }
  // TODO(kjlubick): more data processing
  return arr;
}




const colMap = {
  'name': (task, ele) => {
    let name = task.name;
    if (!ele._verbose && task.name.length > 80) {
      name = name.slice(0, 77) + '...';
    }
    return html`<a href="example.com">${name}</a>`;
  }
}