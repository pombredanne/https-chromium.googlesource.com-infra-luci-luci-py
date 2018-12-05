# Monitoring

Monitoring is done in two parts: capacity and throughput.

Capacity is the bots and what they are doing. Are they dead, continously
rebooting?

Throughput is the tasks that are enqueued and executually executed.


## Capacity

Swarming is designed to work towards 20k bots. To get data at a granularity of 1
minute, this means aggregating data of 33bots per second on a continuous basis.


### Design

The way to achieve this is to precompute as much data in the current handlers,
so that the computation handler collects the data, and fill the holes.


## Throughput

Task rate is much lower than capacity, due to the kind of workload that are run
on Swarming; they generally last several seconds, if not several minutes.
