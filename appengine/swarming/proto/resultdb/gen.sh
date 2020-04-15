#!/bin/bash
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
set -eux

cd $(dirname $0)

# Take revision from
# https://chromium.googlesource.com/infra/luci/luci-go/+log/HEAD/resultdb/proto
revision=7c33ecc8bb3c35ecd473dcbe52edeffd3ffaf643

for f in rpc/v1/invocation.proto rpc/v1/predicate.proto type/common.proto
do
    curl "https://chromium.googlesource.com/infra/luci/luci-go/+/${revision}/resultdb/proto/${f}?format=TEXT" | base64 -d > go.chromium.org/luci/resultdb/proto/"${f}"
done

pwd
../../../components/tools/compile_proto.py --proto_path . .
