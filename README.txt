Visualize disk usage with webtreemap

There are plenty of graphical tools to do this (e.g. Baobab, KFileLight),
but they are typically slow and/or inconvenient (consider a GUI-less server).
I often find myself running du on the command line (over ssh) and wishing
for something more visual.

Enter du2webtreemap!

    ssh someserver du /path/to/somewhere > du.txt
    du2webtreemap < du.txt > du.js
    xdg-open ./du.html

Or run ./demo.sh to see something quick and local.

You'll need webtreemap (https://github.com/martine/webtreemap), which is
conveniently available as a git submodule; after cloning webtreemap-du run

    git submodule init
    git submodule update

Experiment 1: visualising disk usage in an HTML page.


