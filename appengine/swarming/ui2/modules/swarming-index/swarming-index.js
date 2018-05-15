
// TODO(kjlubick): move this to common
function upgradeProperty(ele, prop) {
  if (ele.hasOwnProperty(prop)) {
    let value = ele[prop];
    delete ele[prop];
    ele[prop] = value;
  }
}

import { html, render } from 'lit-html/lib/lit-extended'

// Don't use html for a straight string template, otherwise, it shows up
// as [object Object] when used as the href attribute.
const instancesURL = (ele) => `https://console.cloud.google.com/appengine/instances`+
    `project=${ele._project_id}&versionId=${ele._server_details.server_version}`

const errorsURL = (project_id) =>
    `https://console.cloud.google.com/errors?project=${project_id}`

const logsURL = (project_id) =>
    `https://console.cloud.google.com/logs/viewer?filters=status:500..599&project=${project_id}`

const template = (ele) => html`
<swarming-app client_id$="${ele.client_id}"
              testing_offline$=${ele.testing_offline ? "testing_offline": "  should be space  "}>
  <header>
    <div class=title>Swarming Server</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/tasklist>Task List</a>
      </aside>
  </header>
  <main>

    <h2>Service Status</h2>
    <div>Server Version: ${ele._server_details.server_version}</div>
    <div>Bot Version: ${ele._server_details.bot_version} </div>
    <ul>
      <li>
        <!-- TODO(kjlubick) convert these linked pages to new UI-->
        <a href=/stats>Usage statistics</a>
      </li>
      <li>
        <a href=/restricted/mapreduce/status>Map Reduce Jobs</a>
      </li>
      <li>
        <a href=${instancesURL(ele)}>View version's instances on Cloud Console</a>
      </li>
      <li>
        <a><a href=${errorsURL(ele._project_id)}>View server errors on Cloud Console</a></a>
      </li>
      <li>
        <a><a href=${logsURL(ele._project_id)}>View logs for HTTP 5xx on Cloud Console</a></a>
      </li>
    </ul>

    <h2>Configuration</h2>
    <ul>
      <!-- TODO(kjlubick) convert these linked pages to new UI-->
      <li>
        <a href="/restricted/config">View server config</a>
      </li>
      <li>
        <a href="/restricted/upload/bootstrap">View/upload bootstrap.py</a>
      </li>
      <li>
        <a href="/restricted/upload/bot_config">View/upload bot_config.py</a>
      </li>
      <li>
        <a href="/auth/groups">View/edit user groups</a>
      </li>
    </ul>

    <div hidden$="[[_cannotBootstrap(_permissions)]]">
      <h2>Bootstrapping a bot</h2>
      To bootstrap a bot, run one of these (all links are valid for 1 hour):
      <ol>
        <li>
          <strong> TL;DR; </strong>
<pre class="command">python -c "import urllib; exec urllib.urlopen('[[_host_url]]/bootstrap?tok=[[_bootstrap_token]]').read()"</pre>
        </li>
        <li>
          Escaped version to pass as a ssh argument:
<pre class="command">'python -c "import urllib; exec urllib.urlopen('"'[[_host_url]]/bootstrap?tok=[[_bootstrap_token]]'"').read()"'</pre>
        </li>
        <li>
          Manually:
<pre class="command" style="margin-bottom:0">mkdir bot; cd bot
rm -f swarming_bot.zip; curl -sSLOJ [[_host_url]]/bot_code?tok=[[_bootstrap_token]]
python swarming_bot.zip</pre>
        </li>
      </ol>
    </div>
  </main>
  <footer><error-sk></error-sk></footer>
</swarming-app>`;

window.customElements.define('swarming-index', class extends HTMLElement {
  constructor() {
    super();
    this._server_details = {
      server_version: '12345-deadbeef',
      bot_version: 'abcdoeraymeyouandme',
    };
    let idx = location.hostname.indexOf('.appspot.com');
    this._project_id = location.hostname.substring(0, idx) || 'not_found';
  }

  connectedCallback() {
    upgradeProperty(this, 'client_id');
    upgradeProperty(this, 'testing_offline');

    this._render();
  }

  _render() {
    render(template(this), this);
  }

});
