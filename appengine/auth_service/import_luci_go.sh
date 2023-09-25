#!/bin/bash
# Copyright 2023 The LUCI Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copies some protos from luci-go, assuming infra.git gclient
# layout. Generates Makefile and _pb2.py.

set -e

MYPATH=$(dirname "${BASH_SOURCE[0]}")
cd ${MYPATH}

LUCI_GO=../../../go/src/go.chromium.org/luci/
# LUCI_GO_COMMON_PROTOS_DIR=${LUCI_GO}/common/proto/
# LUCI_GO_PROTOCOL_PROTOS_DIR=${LUCI_GO}
LUCI_GO_CONFIG_PROTOS_DIR=${LUCI_GO}/auth_service/api/configspb
PROTO_TEMP_DIR=${MYPATH}/proto/tempconfig

# Kill all existing files.
rm -rf proto/tempconfig
rm -f proto/config*
mkdir proto/tempconfig

# Copy fresh files.
cp ${LUCI_GO_CONFIG_PROTOS_DIR}/config.proto ./proto/tempconfig/

touch ./proto/tempconfig/__init__.py

# Make proto import paths relative to the new root.
sed -i '' 's|import "go.chromium.org/luci/server/auth/service/protocol/components/auth/proto/|import "components/auth/proto/|g' ./proto/tempconfig/*.proto
# sed -i '' 's|import "go.chromium.org/luci/common/proto/|import "swarming/bb/go/chromium/org/luci/common/proto/|g' ./auth_service/proto/*.proto
sed -i '' 's|package auth.configs|package auth_service|g' ./proto/tempconfig/*.proto

# Put the revision of copied files into generate.go for posterity.
luci_go_rev=$(git -C ${LUCI_GO} rev-parse HEAD)

sed -i  -e "s|# Commit:.*|# Commit:${luci_go_rev}|g" ./Makefile

# Generate *.pb2.py.
Make

cp ${PROTO_TEMP_DIR}/* ./proto/

rm -rf ./proto/tempconfig