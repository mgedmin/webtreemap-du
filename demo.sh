#!/bin/sh
du . | python du2webtreemap.py -d 'webtreemap-du' -p > du.js
if [ -f webtreemap/webtreemap.js ]; then
    echo 'Now open ./du.html in a web browser.'
else
    echo 'Now fetch webtreemap with'
    echo '  git submodule init'
    echo '  git submodule update'
    echo 'then open ./du.html in a web browser.'
fi
