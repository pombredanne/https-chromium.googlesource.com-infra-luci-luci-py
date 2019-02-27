FROM gcr.io/chrome-infra-spinnaker/infra as builder

RUN  gclient sync && cd /infra && \
     git checkout master && git pull --recurse-submodules
RUN  mkdir -p /infra_shallow/infra && cd /infra_shallow && \
     git clone --depth=1 file:////infra ./infra && \
     rm -rf /infra && \
     mv /infra_shallow/* /


FROM gcr.io/chrome-infra-spinnaker/infra
COPY --from=builder /infra /infra
RUN  cd /infra/luci && git checkout master
COPY Makefile /infra/luci/appengine/config_service/
COPY Makefile_proto /infra/luci/appengine/config_service/components/config/proto/Makefile
COPY app.yaml /infra/luci/appengine/config_service/
COPY __init__.py /infra/luci/appengine/config_service/gae_ts_mon
COPY module-backend.yaml /infra/luci/appengine/config_service/
# The external_deps make target should fetch any external dependencies.
# This so nothing needs to be fetched into the build Docker image.
RUN  cd /infra/luci/appengine/config_service && make external_deps
RUN  mkdir /workspace
ENV  TARDIR /workspace
RUN  rm /infra/luci/appengine/config_service/tools/protoc
WORKDIR /infra/luci/appengine/config_service
CMD  ["make", "package"]
