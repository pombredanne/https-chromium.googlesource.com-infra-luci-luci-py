# Monitoring

Monitoring is done in two parts: capacity and throughput.

Capacity is the bots and what they are doing. Are bots efficient, mostly dead,
or wasting their time either continously rebooting or running bot\_config hooks?

Throughput is the tasks that are enqueued and executed. Are tasks pending for
long, deduped at a good rate?


## Capacity

Swarming is designed to work towards 20k bots. To get data at a granularity of 1
minute, this means aggregating data of 33 bots per second on a continuous basis.


### Design

The way to achieve this is to precompute as much data in the current handlers,
so that the computation handler collects the data, and fill the holes.


## Throughput

Swarming is designed to work at a rate of 20 tasks created per second. In
practice task rate is much lower due to the kind of workload that are run on
Swarming; they generally last several seconds, if not several minutes or hours.
