# Python pRPC Implementation

This directory contains an implementation of pRPC for Python. For more details
on pRPC, please visit [the pRPC
docs.](https://godoc.org/go.chromium.org/luci/grpc/prpc).

## Caveats

Currently, the Python pRPC implementation only supports unary-unary calls, that
is, RPC calls that take and return exactly one argument.
