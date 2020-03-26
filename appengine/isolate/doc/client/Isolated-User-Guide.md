# `isolated` user guide

Archive and run your isolated test.


## Introduction

-   The Go binary `isolated` (compiled from
    https://chromium.googlesource.com/infra/luci/luci-go/+/refs/heads/master/client/cmd/isolated/main.go)
    is meant to replace `isolateserver.py`.
-   `isolated` is the client side code relating to isolated executable. Use it
    directly for low-level archival and retrieval.


## Overview

  - "`isolated help`" gives you all the help you need so only a quick
    overview is given here.
  - "`isolate archive`" is a shortcut to compile a `.isolate` into a
    `.isolated` file *and* archive the tree to an Isolate Server. If you already
    have a `.isolated` file, use "`isolated archive`" directly.


### Archiving

If you want to upload a test to the isolate server, you want the first command:

  - Archive an .isolate tree: "`isolate archive -isolate <.isolate> -isolated
    <.isolated> -isolate-server https://host`"
  - Archive a single file: "`isolated archive -files <file> -isolate-server
    https://host`"


### Downloading

A common use case is when a Continuous Integration builder or a Pre Commit
builder archived a build that you want to investigate locally.


#### CLI

  - Fetch the whole isolated tree : "`isolated download -isolated
    <.isolated> -isolate-server https://host` "
  - Fetch a single file: "`isolated download -isolated <hash> -output-dir
    <destination> -isolate-server https://host`"


#### Cache

"`isolated download`" supports the flag `-cache` which keeps a local
cache, to speed up repetitive downloads.


#### Web

  - Browsing any file via `https://host/browse`.


### Running an isolated test

  - Run test archived on an isolate server: "`run_isolated.py --hash <.isolated
    sha1> --isolate-server https://host`"
  - Use `run_isolated.py --help` for more information.

Note that `run_isolated.py` will automatically create a local cache on your
behalf, similar to the optional `--cache` flag to `isolated download`.
*If you do not want this*, do not use `run_isolated.py`. Use "`isolated
download`" and run the command manually.
