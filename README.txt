Experiments with webtreemap (see https://github.com/martine/webtreemap#readme)

Experiment 1: visualising disk usage in an HTML page.

    du /path/to/somewhere > du.txt
    du2webtreemap < du.txt > du.js
    xdg-open ./du.html

