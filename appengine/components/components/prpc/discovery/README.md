# Discovery API

`service.proto` was imported from 
`go.chromium.org/luci/grpc/discovery/service.proto` at revision
`a2bc84c495e277aaf6c17dcdbf8be727ce23deee`.

## Regenerating Python from Protocol Buffers

In order to regenerate the python server and client stubs from the `.proto`
files, follow these steps:

```
$ pip install grpcio grpcio-tools  # may need to be 'sudo pip'
$ python -m grpc.tools.protoc --proto_path=. --python_out=. --grpc_python_out=.
*.proto
```
