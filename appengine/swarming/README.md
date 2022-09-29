# Swarming

An AppEngine service to do task scheduling on highly hetegeneous fleets at
medium (10000s) scale. It is focused to survive network with low reliability,
high latency while still having low bot maintenance, and no server maintenance
at all since it's running on AppEngine.

Swarming is purely a task scheduler service. File I/O is done through
[RBE-CAS](http://shortn/_6VZrqG0zDU) (google internal) .

[Documentation](doc)


## Chrome Operations release

Visit https://goto.google.com/swarming-releases for the Chrome Operations
release process.


## Setting up

*   Visit http://console.cloud.google.com and create a project. Replace
    `<appid>` below with your project id.
    *   App Engine
        *   Enable it and choose `us-central`.
    *   IAM & Admin > IAM
        *   Click `Add Member` and add someone else so you can safely be hit by
            a bus.
    *   APIs & Services > Credentials
        *   Create a new `OAuth client ID`.
        *   Click `Configure consent screen` if required.
            *   Use the Swarming LUCY mascot.
            *   Set Authorized domains to `<appid>.appspot.com`
            *   Set Application Homepage link and Privacy Policy link to
                `https://<appid>.appspot.com`.
            *   Click `Save`. You need to create the token before requesting
                validation...
        *   Choose Application type `Web application`.
        *   Set Authorized JavaScript origins to `https://<appid>.appspot.com`.
        *   Set Authorized redirect URIs to `https://<appid>.appspot.com/oauth2callback`.
        *   Click `Create`.
        *   Replace \<client_id\> below with the created client id.
    *   Pub/Sub
        *   Click `Enable API`.
    *   App Engine > Memcache
        *   Click `Change`.
        *   Chose `Dedicated`.
        *   Set the cache to Dedicated 1Gb.
        *   Wait a day of steady state usage.
        *   Set the limit to be lower than the value read at "Total cache
            size" in "Memcache Viewer".
    *   App Engine > Settings
        *   Click `Edit`:
        *   Set Google login Cookie expiration to: 2 weeks.
        *   Click `Save`.
*   Upload the code with: `./tools/gae upl -x -A <appid>`
*   Run [setup_bigquery.sh](setup_bigquery.sh) to create the BigQuery
    `swarming.*` tables and grant write access to the AppEngine app. The cron
    job will fail meanwhile.
*   If you plan to use a [config service](../config_service) (the normal case):
    *   Make sure it is setup already.
    *   Make sure you set
        [SettingsCfg.ui_client_id](proto/config/config.proto)
        to be \<client_id\>
    *   [Follow instruction
        here](../components/components/config/#linking-to-the-config-service).
*   If you are not using a config service, see [Configuring using FS
    mode](../components/components/config/README.md#fs-mode).
    *   You'll need to add an entry to settings.cfg like `ui_client_id:
        "<client_id>"`
    *   You also need to update chrome-infra-auth/oauth.cfg to add `client_ids:
        "<client_id>"`
*   If you plan to use an [auth_service](../auth_service),
    *   Make sure it is setup already.
    *   [Follow instructions here](../auth_service#linking).
*   Else, visit https://\<appid\>.appspot.com/auth/bootstrap and click
    `Proceed`.
*   Visit "_https://\<appid\>.appspot.com/auth/groups_":
    *   Create [access groups](doc/Access-Groups.md) as relevant.
*   Configure [bot_config.py](swarming_bot/config/bot_config.py) and
    [bootstrap.py](swarming_bot/config/bootstrap.py) as desired. Both are
    optional.
*   Visit "_https://\<appid\>.appspot.com_" and follow the instructions to start
    a bot.
*   Visit "_https://\<appid\>.appspot.com/botlist_" to ensure the bot is
    alive.
*   Run one of the [examples in the client code](../../client/example).

## Running Tests

In order to run the tests `python` on your `$PATH` should point to python `2.7`.
Tests `local_smoke_test.py` rely on executing `python2` specific code for some tests.

The entire test suite may be run using the following command:

```sh
vpython -vpython-spec <path-to>/infra/luci/.vpython -u test.py -v --conf unittest.cfg
```

Many of the test suites can also be run independently, by running `./<module_name>_test.py`. This will typically invoke the tests using `vpython`.

Appending `-v` to the test suite will force verbose output of tests, showing a more complete `diff` for test failures.

The test suite `local_smoke_test.py` contains a number of local integration tests which are end to end but running locally.
`local_smoke_test.py` will typically create a number of logs which are deleted after the tests are finished running located in the `/tmp/local_smoke_test*/` directory.
To prevent those logs from being deleted you can run `local_smoke_test.py --leak`.

To run a specific test, most test suites allow for `./<module_name>_test.py <TestSuiteClass>.<test_name>` eg:

```sh
./local_smoke_test.py Test.test_with_cas
```


## Running locally

You still need an OAuth2 client id if you want to use the Web UI:

*   Visit http://console.cloud.google.com and create a project.
*   Visit Google Cloud Console
    *   APIs & Services > Credentials
        *   Create a new "Oauth 2.0 Client Id" of type "web application". Make
            sure `http://localhost:9050` is an authorized JavaScript origin
            and `http://localhost:9050/oauth2callback` is an authorized
            redirect URL. You can add multiple ports as needed. 9050 is the
            default port used by `start_server.py`. Replace \<client_id\> below
            with the created client id. It will look like
            `012345678901-abcdefghijklmnopqrstuvwxyzabcdef.apps.googleusercontent.com`.
        *   You will have to do the 'consent' flow.
*   Configure to use this client ID [using FS
    mode](../components/components/config/README.md#fs-mode).
    Create `configs/services/swarming-local/CONFIGS/settings.cfg` with:

          mkdir -p configs/services/swarming-local/CONFIGS/
          echo 'ui_client_id: "<client_id>"' > configs/services/swarming-local/CONFIGS/settings.cfg

*   If you want to access it from another workstation, since the cliend id is
    allowed to localhost, you can `ssh workstation -L 9050:localhost:9050`.
    Make sure that any corp proxy is bypassed as needed.

You can run a swarming+RBE-CAS local setup with:

    ./tools/start_servers.py

Then run a bot with:

    ./tools/start_bot.py http://localhost:9050

