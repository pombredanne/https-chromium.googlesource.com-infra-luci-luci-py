#!/bin/bash

cd $(dirname $0)

if [ $# != 1 ]; then
    echo "usage: $ $0 <version>"
    echo "e.g. $ $0 2.21.0"
    exit 1
fi

version="${1}"

find . | fgrep '/' | fgrep -v './update.sh' | fgrep -v 'README.swarming' | \
    sort -r | xargs rm -r
curl -sL https://github.com/psf/requests/archive/v${version}.tar.gz | \
    tar xvz --strip-components 2 requests-${version}/requests
