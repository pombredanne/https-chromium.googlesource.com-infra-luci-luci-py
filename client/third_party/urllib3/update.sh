#!/bin/bash

cd $(dirname $0)

if [ $# != 1 ]; then
    echo "usage: $ $0 <version>"
    echo "e.g. $ $0 1.24.1"
    exit 1
fi

version="${1}"

find . | fgrep '/' | fgrep -v './update.sh' | fgrep -v 'README.swarming' | \
    sort -r | xargs rm -r
curl -sL https://github.com/urllib3/urllib3/archive/${version}.tar.gz | \
    tar xvz --strip-components 3 urllib3-${version}/src/urllib3
