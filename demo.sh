#!/bin/sh
du . | python3 du2webtreemap.py -d 'webtreemap-du' -p --html > du.html
echo 'Now open ./du.html in a web browser.'
