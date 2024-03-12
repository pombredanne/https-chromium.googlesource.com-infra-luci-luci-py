# proto

Contains protobuf definitions:

  * [config/](config/): Swarming LUCI Config schemas.
  * [api/](api/): public APIs (BigQuery Schema, pRPC API).
  * [internals/](internals/): internal APIs used by Swarming itself.

These protos are also exported into luci-go.git [here].

[here]: https://chromium.googlesource.com/infra/luci/luci-go/+/refs/heads/main/swarming/proto/

Protobuf definitions that are imported from luci-go:
  * [notifications/](notifications/): Swarming PubSub notifications related.
    It's only used internally by Swarming and should not be exported to users.