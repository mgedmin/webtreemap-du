#!/bin/sh
du . | python3 du2webtreemap.py -d 'webtreemap-du' -p --html > du.html
if ! [ -f webtreemap/webtreemap.js ]; then
    echo 'Fetching webtreemap...'
    git submodule update --init
fi
echo 'Now open ./du.html in a web browser.'
