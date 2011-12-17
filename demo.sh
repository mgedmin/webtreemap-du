#!/bin/sh
du . | python du2webtreemap.py -d 'webtreemap-du' -p > du.js
echo 'Now open ./du.html in a web browser.'
