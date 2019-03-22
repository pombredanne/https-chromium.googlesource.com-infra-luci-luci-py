# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
#

TARDIR ?= "/workspace"

build: compile-proto

compile-proto:
	cd components/config/proto && make

test: build
	tools/run_coverage.py

deploy_dev-gae: build
	tools/gae upload -x -A luci-config-dev

deploy-gae: build
	tools/gae upload -x -A luci-config

deploy:
	gcloud builds submit --substitutions=_PROJECT_DIR=luci/appengine/config_service --config cloudbuild.yaml . --project chrome-infra-spinnaker
	echo "Follow deployment at: go/luci-config-spin"

deploy-dev: build
	$(eval GCBDIR := $(shell mktemp -d -p /tmp luci-config.XXXX))
	# The protoc symlink points to nowhere.
	# Is that expected?
	rsync -aLK --exclude="tools/protoc" . $(GCBDIR)
	cd $(GCBDIR) && gcloud builds submit --config cloudbuild-dev.yaml . --project chrome-infra-spinnaker
	rm -fr $(GCBDIR)
	echo "Follow deployment at: go/luci-config-spin"

external_deps:
	cd ui && make

package_release:
	rsync -aLK . $(TARDIR)/package
