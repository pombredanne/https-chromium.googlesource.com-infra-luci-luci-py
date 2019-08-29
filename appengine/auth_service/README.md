# Auth Service

Auth Service centrally manages and distributes data and configuration involved
in authentication and authorization decisions performed by services in a LUCI
deployment.

It is part of the control plane, and as such it is **not directly involved** in
authorizing every request to LUCI. Auth Service merely tells other services
how to do it, and they do it themselves.

If Auth Service becomes unavailable, everything remains operational, except
the authentication and authorization configuration becomes essentially "frozen"
until Auth Service comes back online and resumes updating it.


## Configuration distributed by Auth Service (aka AuthDB)

This section describes what exactly is meant by "data and configuration
involved in authentication and authorization". See
[AuthDB](../components/components/proto/replication.proto) proto for all
details.

### Groups graph

...

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
Alternatively, read [source code](../components/components/auth/ui/rest_api.py).

This API is appropriate for modifying groups and for adhoc checks when debugging
access errors. Both these activities can be done through web UI.

Services that care about availability **must not** use this API for
authorization checks. It has no performance or availability guarantees.

Instead such services should use AuthDB replication protocol to obtain (and
keep up-to-date) the snapshot of all groups, so they can use it locally without
hitting Auth Service on every request.


### AuthDB replication protocol

...


## Configuration files

...



## Hooking up a LUCI service to receive AuthDB updates




## External dependencies

Auth Service depends on following services:
  * App Engine standard: the serving environment.
  * Cloud Datastore: storing the state (including groups graph).
  * Cloud PubSub: sending AuthDB update notifications to clients.
  * Cloud Storage: saving AuthDB dumps to be consumed by clients.
  * Cloud IAM: managing PubSub topic ACLs to allow clients to subscribe.
  * LUCI Config: receiving own configuration files.
