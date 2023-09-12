#!/bin/bash
# Copyright 2020 The LUCI Authors.
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

LUCI_GO=../../../../go/src/go.chromium.org/luci/
LUCI_GO_PROTOS_DIR=${LUCI_GO}/auth_service/api/configspb

# Kill all existing files.
rm -f config*
rm -f Makefile

# Copy fresh files.
cp \
  ${LUCI_GO_PROTOS_DIR}/config.proto \
  \
  .

# Make proto import paths relative to the new root.
sed -i '' 's|import "go.chromium.org/luci/server/auth/service/protocol/components/auth/proto/|import "components/auth/proto/|g' ./*.proto

# Put the revision of copied files into generate.go for posterity.
luci_go_rev=$(git -C ${LUCI_GO} rev-parse HEAD)

cat <<EOF >> Makefile
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

# Files copied from https://chromium.googlesource.com/infra/go/src/go.chromium.org/luci:
#   server/auth/service/protocol/realms.proto
#   server/auth/service/protocol/replication.proto
#   server/auth/service/protocol/security_config.proto
#
# Commit: ${luci_go_rev}
# Modifications: see import_luci_go.sh

compile_config:
	# If we simply compile *.proto files relative to this dir, the recorded file
	# names in the generated _pb2.py are relative to this dir too which may
	# introduce naming collisions in the protobuf registry.
	#
	# Move the proto path to //appengine/components to "namespace" proto files.
	# This is consistent with other components assuming that "components" is in
	# the import path.
	../tools/compile_proto.py --proto_path=../  config.proto
compile_realms_config:
	# If we simply compile *.proto files relative to this dir, the recorded file
	# names in the generated _pb2.py are relative to this dir too which may
	# introduce naming collisions in the protobuf registry.
	#
	# Move the proto path to //appengine/components to "namespace" proto files.
	# This is consistent with other components assuming that "components" is in
	# the import path.
	../tools/compile_proto.py realms_config.proto
EOF

# Generate *.pb2.py.
Make compile_config
