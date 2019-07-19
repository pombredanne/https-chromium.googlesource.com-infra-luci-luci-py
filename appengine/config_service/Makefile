# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
#

TARDIR ?= "/workspace"
define FILEBUG

\e[31m
If you're using gae.py due to deploy/deploy_dev targets not working
please file a bug at:

https://bugs.chromium.org/p/chromium/issues/entry?components=Infra%3EProdTech%3EReleases

If not, please use the deploy/deploy_dev targets.
\e[0m

endef
export FILEBUG

SPIN = $(shell command -v spin 2> /dev/null)

build: compile-proto

compile-proto:
	cd components/config/proto && make

test: build
	@echo -e "$$FILEBUG"
	tools/run_coverage.py

# deploy_dev-gae deploys to the dev environmant using gae.py.
# When using this due to deploy/deploy_dev targets not working, please file a bug at:
#
# https://bugs.chromium.org/p/chromium/issues/entry?components=Infra%3EProdTech%3EReleases
deploy_dev_gae: build
	@echo -e "$$FILEBUG"
	tools/gae upload -x -A luci-config-dev

# deploy_dev-gae deploys to prod using gae.py.
# When using this due to deploy/deploy-dev targets not working, please file a bug at:
#
# https://bugs.chromium.org/p/chromium/issues/entry?components=Infra%3EProdTech%3EReleases
deploy_gae: build
	@echo -e "$$FILEBUG"
	tools/gae upload -x -A luci-config

# deploy sends the currently submitted version off to Spinnaker for deployment.
# Spinnaker will first deploy to staging and then prod.
#
# See go/luci-config-spin for Spinnaker pipeline status.
deploy:
ifeq ($(SPIN),)
	$(error "please install spin go/chops-install-spin")
endif
	$(SPIN) pipeline execute --name "Deploy Luciconfig" --application luciconfig
	@echo "Follow progress here: https://spinnaker-1.endpoints.chrome-infra-spinnaker.cloud.goog/#/applications/luciconfig/executions"

# deploy_dev packs up the current folder and sends it off to Spinnaker for release to the Dev environment.
#
# See go/luci-config-spin for Spinnaker pipeline status.
deploy_dev: build
	$(eval GCB_DIR:= $(shell mktemp -d -p /tmp monorail_XXXXX))
	rsync -aLK . $(GCB_DIR)  # Dereferences symlinks before snapshotting.
	cd $(GCB_DIR) && tar cf ${_VERSION}.tar .
	gsutil cp $(GCB_DIR)/${_VERSION}.tar gs://chrome-infra-builds/luci-config/dev
	rm -rf $(GCB_DIR)
	@echo "Follow deployment at: go/luci-config-spin"


# external_deps fetches and builds external depencencies.
# This is run but GCB in the build stage.
external_deps:
	cd ui && make

# package_release packages the current folder to TARDIR.
package_release:
	rsync -aLK . $(TARDIR)/package
