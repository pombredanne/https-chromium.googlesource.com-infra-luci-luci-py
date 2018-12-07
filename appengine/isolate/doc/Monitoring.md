# Monitoring

The isolate server monitors the lookups, uploads and downloads. It doesn't
monitor the effective cache hit rate on lookups yet.

The BigQuery definition is in [isolated.proto](../proto/isolated.proto) as a
series of StatsSnapshot.

Use `bq` from gcloud SDK to create the dataset, keeping data for 2 years:

Warning: On first `bq` invocation, it'll try to find out default credentials and
will ask to select a default app; just press enter to not select a default.

```
APPID=isolateserver-dev
bq --location=US mk --dataset --default_table_expiration 63244800 --description 'Isolate server data' ${APPID}:isolated
```

Use `bqschemaupdater` from
[infra.git](https://chromium.googlesource.com/infra/infra.git/+/master/go/) to
populate the BigQuery schema from isolated.proto.

Warning: On first `bqschemaupdater` invocation, it'll request default
credentials which is stored independently than `bq`.

```
cd proto
bqschemaupdater -message isolated.StatsSnapshot -table ${APPID}.isolated.stats
```
