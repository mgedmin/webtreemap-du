#!/bin/sh
du . | python3 du2webtreemap.py -d 'webtreemap-du' -p --html > du.html
echo 'Now opening ./du.html in a web browser.'
xdg-open du.html
