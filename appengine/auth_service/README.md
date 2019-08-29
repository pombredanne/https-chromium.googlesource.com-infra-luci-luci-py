# Auth Service

Auth Service centrally manages and distributes data and configuration involved
in authentication and authorization decisions performed by services in a LUCI
deployment. It is part of the control plane, and as such it is **not directly
involved** in authorizing every request to LUCI. Auth Service merely tells other
services how to do it, and they do it themselves.

If Auth Service becomes unavailable, everything remains operational, except
the authentication and authorization configuration becomes essentially "frozen"
until Auth Service comes back online and resumes updating it.


## Configuration distributed by Auth Service (aka AuthDB)

This section describes what exactly is meant by "data and configuration
involved in authentication and authorization". See AuthDB message in
[replication.proto](../components/components/auth/proto/replication.proto) for
all details.

### Groups graph

Groups are how the lowest layer of ACLs is expressed in LUCI, e.g. a service
may authorize some action to members of some group. Each group has a name
(global to the LUCI deployment), a list of identities it includes directly,
a list of nested groups, and a list of glob-like patterns to match against
identity strings.

An identity string encodes a principal that performs an action. It's the result
of the authentication. It has a form `<type>:<id>` and can represent:
  * `user:<email>` - Google Accounts (end users and service accounts).
  * `anonymous:anonymous` - callers that didn't provide any credentials.
  * `bot:<hostname>` - used only by Swarming, individual bots pulling tasks.
  * `bot:whitelisted-ip` - callers authenticated exclusively through IP
    whitelist. **Deprecated**.
  * `service:<app-id>` - GAE application authenticated via
    `X-Appengine-Inbound-Appid` header. **Deprecated**.


### IP whitelists

...

### OAuth client ID whitelist

...

### Security configuration for internal LUCI RPCs.

...


## API surfaces

### Groups API

This is a REST API to examine and modify groups graph. It is used primarily by
Auth Service's own web frontend (i.e. it is used primarily by humans). It is
documented [right there](https://chrome-infra-auth.appspot.com/auth/api).
Alternatively, read the
[source code](../components/components/auth/ui/rest_api.py). This API is
appropriate for modifying groups and for adhoc checks when debugging
access errors (and both these activities can be done through the web UI, so
there's rarely a need to use this API directly).

Services that care about availability **must not** use this API for
authorization checks. It has no performance or availability guarantees. If you
use this API, and your service goes down because Auth Service is down, it is
**your fault**.

Instead services should use AuthDB replication protocol to obtain (and keep
up-to-date) the snapshot of all groups, to use it locally without hitting Auth
Service on every request. See the next section for more information.


### AuthDB replication protocol

...


### Hooking up a LUCI service to receive AuthDB updates

...


## Configuration files

...


## External dependencies

Auth Service depends on following services:
  * App Engine standard: the serving environment.
  * Cloud Datastore: storing the state (including groups graph).
  * Cloud PubSub: sending AuthDB update notifications to authorized clients.
  * Cloud Storage: saving AuthDB dumps to be consumed by authorized clients.
  * Cloud IAM: managing PubSub ACLs to allow authorized clients to subscribe.
  * LUCI Config: receiving own configuration files.
