#!/bin/sh
du . | python du2webtreemap.py -d 'webtreemap-du' -p > du.js
if ! [ -f webtreemap/webtreemap.js ]; then
    echo 'Fetching webtreemap...'
    git submodule update --init
fi
echo 'Now open ./du.html in a web browser.'
