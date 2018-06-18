// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import 'modules/bot-list'
import { deepCopy } from 'common-sk/modules/object'

import { data_s10 } from   'modules/bot-list/test_data'
import { column, processBots } from 'modules/bot-list/bot-list-helpers'

describe('bot-list', function() {

  const fetchMock = require('fetch-mock');

  beforeEach(function(){
    fetchMock.sandbox();

    // TODO(kjlubick): This will need to be a regex at some point
    fetchMock.get('/_ah/api/swarming/v1/bots/list', data_s10);

    // Everything else
    fetchMock.catch(404);
  });

  afterEach(function() {
    // Completely remove the mocking which allows each test
    // to be able to mess with the mocked routes w/o impacting other tests.
    fetchMock.restore();
  });

  // A reusable HTML element in which we create our element under test.
  let container = document.createElement('div');
  document.body.appendChild(container);

  afterEach(function() {
    container.innerHTML = '';
  });

  beforeEach(function() {
    // Fix the time so all of our relative dates work.
    jasmine.clock().install();
    jasmine.clock().mockDate(new Date(Date.UTC(2018, 5, 14, 12, 46, 22, 1234)));
  });

  afterEach(function() {
    jasmine.clock().uninstall();
  })

  // calls the test callback with one element 'ele', a created <swarming-index>.
  // We can't put the describes inside the whenDefined callback because
  // that doesn't work on Firefox (and possibly other places).
  function createElement(test) {
    return window.customElements.whenDefined('bot-list').then(() => {
      container.innerHTML = `<bot-list client_id=for_test testing_offline=true></bot-list>`;
      expect(container.firstElementChild).toBeTruthy();
      test(container.firstElementChild);
    });
  }

  function userLogsIn(ele, callback) {
    // The swarming-app emits the 'busy-end' event when all pending
    // fetches (and renders) have resolved.
    ele.addEventListener('busy-end', (e) => {
      callback();
    });
    let login = ele.querySelector('oauth-login');
    login._logIn();
    fetchMock.flush();
  }

//===============TESTS START====================================

  describe('html structure', function() {
    it('contains swarming-app as its only child', function(done) {
      createElement((ele) => {
        expect(ele.children.length).toBe(1);
        expect(ele.children[0].tagName).toBe('swarming-app'.toUpperCase());
        done();
      });
    });

    // TODO(kjlubick): handle not logged in case
    xdescribe('when not logged in', function() {
      it('tells the user they should log in', function(done) {
        createElement((ele) => {
          let serverVersion = ele.querySelector('swarming-app>main .server_version');
          expect(serverVersion).toBeTruthy();
          expect(serverVersion.innerText).toContain('must log in');
          done();
        })
      })
      it('does not display filters or bots', function(done) {
        createElement((ele) => {
          // TODO
          expect(false).toBeTruthy();
          done();
        })
      });
    });

    describe('when logged in as user (not admin)', function() {

      describe('default landing page', function() {
        it('displays whatever bots show up', function(done) {
          createElement((ele) => {
            userLogsIn(ele, () => {
              let botRows = ele.querySelectorAll('.bot-table .bot-row');
              expect(botRows).toBeTruthy();
              expect(botRows.length).toBe(10, '(num botRows)');
              done();
            });
          });
        });

        it('shows the default set of columns', function(done) {
          createElement((ele) => {
            userLogsIn(ele, () => {
              // ensure sorting is deterministic.
              ele._sort = 'id';
              ele._dir = 'asc';
              ele._verbose = false;
              ele.render();

              let colHeaders = ele.querySelectorAll('.bot-table thead th');
              expect(colHeaders).toBeTruthy();
              expect(colHeaders.length).toBe(4, '(num colHeaders)');

              expect(colHeaders[0].innerText.trim()).toBe('Bot Id');
              expect(colHeaders[1].innerText.trim()).toBe('Current Task');
              expect(colHeaders[2].innerText.trim()).toBe('OS');
              expect(colHeaders[3].innerText.trim()).toBe('Status');

              let rows = ele.querySelectorAll('.bot-table .bot-row');
              expect(rows).toBeTruthy();
              expect(rows.length).toBe(10, '10 rows');

              let cols = ele.querySelectorAll('.bot-table .bot-row td');
              expect(cols).toBeTruthy();
              expect(cols.length).toBe(4 * 10, '4 columns * 10 rows');
              // little helper for readability
              let cell = (r, c) => cols[4*r+c];

              // Check the content of the first few rows (after sorting)
              expect(rows[0]).not.toHaveClass('dead');
              expect(rows[0]).not.toHaveClass('quarantined');
              expect(rows[0]).not.toHaveClass('old_version');
              expect(cell(0, 0).innerText).toBe('somebot10-a9');
              expect(cell(0, 0).innerHTML).toContain('<a ', 'has a link');
              expect(cell(0, 0).innerHTML).toContain('href="/bot?id=somebot10-a9"', 'link is correct');
              expect(cell(0, 1).innerText).toBe('idle');
              expect(cell(0, 1).innerHTML).not.toContain('<a ', 'no link');
              expect(cell(0, 2).innerText).toBe('Ubuntu-17.04');
              expect(cell(0, 3).innerText).toContain('Alive');

              expect(rows[1]).toHaveClass('quarantined');
              expect(cell(1, 0).innerText).toBe('somebot11-a9');
              expect(cell(1, 1).innerText).toBe('idle');
              expect(cell(1, 2).innerText).toBe('Android');
              expect(cell(1, 3).innerText).toContain('Quarantined');
              expect(cell(1, 3).innerText).toContain('[too_hot,low_battery]');

              expect(rows[2]).toHaveClass('dead');
              expect(rows[2]).toHaveClass('old_version');
              expect(cell(2, 0).innerText).toBe('somebot12-a9');
              expect(cell(2, 1).innerText).toBe('3e17182091d7ae11');
              expect(cell(2, 1).innerHTML).toContain('<a ', 'has a link');
              expect(cell(2, 1).innerHTML).toContain('href="/task?id=3e17182091d7ae10"',
                                        'link is pointing to the cannonical (0 ending) page');
              expect(cell(2, 1).innerHTML).toContain('title="Perf-Win10-Clang-Golo',
                                        'Mouseover with task name');
              expect(cell(2, 2).innerText).toBe('Windows-10-16299.431');
              expect(cell(2, 3).innerText).toContain('Dead');
              expect(cell(2, 3).innerText).toContain('Last seen 1w ago');

              expect(rows[3]).toHaveClass('maintenance');
              expect(cell(3, 3).innerText).toContain('Maintenance');
              expect(cell(3, 3).innerText).toContain('Need to re-format the hard drive.');

              expect(rows[4]).toHaveClass('old_version');
              done();
            });
          });
        });

        it('updates the sort-toggles based on the current sort direction', function(done) {
          createElement((ele) => {
            userLogsIn(ele, () => {
              ele._sort = 'id';
              ele._dir = 'asc';
              ele.render();

              let sortToggles = ele.querySelectorAll('.bot-table thead sort-toggle');
              expect(sortToggles).toBeTruthy();
              expect(sortToggles.length).toBe(4, '(num sort-toggles)');

              expect(sortToggles[0].key).toBe('id');
              expect(sortToggles[0].current).toBe('id');
              expect(sortToggles[0].direction).toBe('asc');
              // spot check one of the other ones
              expect(sortToggles[2].key).toBe('os');
              expect(sortToggles[2].current).toBe('id');
              expect(sortToggles[2].direction).toBe('asc');

              ele._sort = 'task';
              ele._dir = 'desc';
              ele.render();

              expect(sortToggles[0].key).toBe('id');
              expect(sortToggles[0].current).toBe('task');
              expect(sortToggles[0].direction).toBe('desc');

              expect(sortToggles[1].key).toBe('task');
              expect(sortToggles[1].current).toBe('task');
              expect(sortToggles[1].direction).toBe('desc');
              done();
            });
          });
        });
      }); // end describe('default landing page')

    });// end describe('when logged in as user')

  }); // end describe('html structure')

  describe('dynamic behavior', function() {
    // This is done w/o interacting with the sort-toggles because that is more
    // complicated with adding the event listener and so on.
    it('can stable sort in ascending order', function(done){
      createElement((ele) => {
        userLogsIn(ele, () => {
          ele._verbose = false;
          // First sort in descending id order
          ele._sort = 'id';
          ele._dir = 'desc';
          ele.render();
          // next sort in ascending os order
          ele._sort = 'os';
          ele._dir = 'asc';
          ele.render();

          let actualOSOrder = ele._bots.map((b) => column('os', b, ele));
          let actualIDOrder = ele._bots.map((b) => b.bot_id);

          expect(actualOSOrder).toEqual(['Android', 'Ubuntu-17.04', 'Ubuntu-17.04', 'Ubuntu-17.04',
            'Ubuntu-17.04', 'Ubuntu-17.04', 'Windows-10-16299.309', 'Windows-10-16299.309',
            'Windows-10-16299.431', 'Windows-10-16299.431']);
          expect(actualIDOrder).toEqual([
            'somebot11-a9', // Android
            'somebot77-a3', 'somebot15-a9', 'somebot13-a9', 'somebot13-a2', 'somebot10-a9', // Ubuntu in descending id
            'somebot17-a9', 'somebot16-a9',   // Win10.309
            'somebot18-a9', 'somebot12-a9']); // Win10.431
          done();
        });
      });
    });

    it('can stable sort in descending order', function(done){
      createElement((ele) => {
        userLogsIn(ele, () => {
          ele._verbose = false;
          // First sort in asc id order
          ele._sort = 'id';
          ele._dir = 'asc';
          ele.render();
          // next sort in descending os order
          ele._sort = 'os';
          ele._dir = 'desc';
          ele.render();

          let actualOSOrder = ele._bots.map((b) => column('os', b, ele));
          let actualIDOrder = ele._bots.map((b) => b.bot_id);

          expect(actualOSOrder).toEqual(['Windows-10-16299.431', 'Windows-10-16299.431',
            'Windows-10-16299.309', 'Windows-10-16299.309', 'Ubuntu-17.04', 'Ubuntu-17.04',
            'Ubuntu-17.04', 'Ubuntu-17.04', 'Ubuntu-17.04', 'Android']);
          expect(actualIDOrder).toEqual([
            'somebot12-a9', 'somebot18-a9', // Win10.431
            'somebot16-a9', 'somebot17-a9', // Win10.309
            'somebot10-a9', 'somebot13-a2', 'somebot13-a9', 'somebot15-a9', 'somebot77-a3',  // Ubuntu in ascending id
            'somebot11-a9']); // Android
          done();
        });
      });
    });
  }); // end describe('dynamic behavior')

  describe('api calls', function() {
    function expectNoUnmatchedCalls() {
      let calls = fetchMock.calls(false, 'GET');
      expect(calls.length).toBe(0, 'no unmatched GETs');
      calls = fetchMock.calls(false, 'POST');
      expect(calls.length).toBe(0, 'no unmatched POSTs');
    }

    it('makes no API calls when not logged in', function(done) {
      createElement((ele) => {
        fetchMock.flush().then(() => {
          // true in the first argument means 'matched calls',
          // that is calls that we expect and specified in the
          // beforeEach at the top of this file.
          let calls = fetchMock.calls(true, 'GET');
          expect(calls.length).toBe(0);
          calls = fetchMock.calls(true, 'POST');
          expect(calls.length).toBe(0);

          expectNoUnmatchedCalls();
          done();
        });
      });
    });

    it('makes auth\'d API calls when a logged in user views landing page', function(done) {
      createElement((ele) => {
        userLogsIn(ele, () => {
          let calls = fetchMock.calls(true, 'GET');
          expect(calls.length).toBe(1, '(num GETs)');
          // calls is an array of 2-length arrays with the first element
          // being the string of the url and the second element being
          // the options that were passed in
          let gets = calls.map((c) => c[0]);
          // TODO(kjlubick): This may need to be a customMatcher or a partial match.
          expect(gets).toContain('/_ah/api/swarming/v1/bots/list');

          // check authorization headers are set
          calls.forEach((c) => {
            expect(c[1].headers).toBeDefined();
            expect(c[1].headers.authorization).toContain('Bearer ');
          })

          calls = fetchMock.calls(true, 'POST');
          expect(calls.length).toBe(0, 'no POSTs on bot-list');

          expectNoUnmatchedCalls();
          done();
        });
      });
    });
  }); // end describe('api calls')

  describe('data parsing', function() {
    const LINUX_BOT = data_s10.items[0];
    const MULTI_ANDROID_BOT = data_s10.items[2];

    it('inflates the state', function() {
      // Make a copy of the object because _processBots will modify it in place.
      let bots = processBots([deepCopy(LINUX_BOT)]);
      expect(bots).toBeTruthy();
      expect(bots.length).toBe(1);
      expect(typeof bots[0].state).toBe('object');
    });

    it('makes a disk cache using the free space of disks', function() {
      // Make a copy of the object because _processBots will modify it in place.
      let bots = processBots([deepCopy(LINUX_BOT)]);
      let disks = bots[0].disks;
      expect(disks).toBeTruthy();
      expect(disks.length).toBe(2, 'Two disks');
      expect(disks[0]).toEqual({id: '/', mb: 680751.3}, 'biggest disk first');
      expect(disks[1]).toEqual({id: '/boot', mb: 842.2});
    });

    it('aggregates the temperatures of the host bot', function() {
      // Make a copy of the object because _processBots will modify it in place.
      let bots = processBots([deepCopy(LINUX_BOT)]);
      let temp = bots[0].state.temp;
      expect(temp).toBeTruthy();
      expect(temp.average).toBe('34.8', 'rounds to one decimal place');
      expect(temp.zones).toBe('thermal_zone0: 34.5 | thermal_zone1: 35', 'joins with |');
    });

    it('turns the device map into a list', function() {
      // Make a copy of the object because _processBots will modify it in place.
      let bots = processBots([deepCopy(MULTI_ANDROID_BOT)]);
      let devices = bots[0].state.devices;
      expect(devices).toBeTruthy();
      expect(devices.length).toBe(3, '3 devices attached to this bot');

      expect(devices[0].serial).toBe('3456789ABC', 'alphabetical by serial');
      expect(devices[0].okay).toBeTruthy();
      expect(devices[0].device_type).toBe('bullhead');
      expect(devices[0].temp.average).toBe('34.4');

      expect(devices[1].serial).toBe('89ABCDEF012', 'alphabetical by serial');
      expect(devices[1].okay).toBeFalsy();
      expect(devices[1].device_type).toBe('bullhead');
      expect(devices[1].temp.average).toBe('36.2');

      expect(devices[2].serial).toBe('Z01234567', 'alphabetical by serial');
      expect(devices[2].okay).toBeFalsy();
      expect(devices[2].device_type).toBe('bullhead');
      expect(devices[2].temp.average).toBe('34.3');
    });
  }); // end describe('data parsing')

});