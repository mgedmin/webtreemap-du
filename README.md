## Visualize disk usage with webtreemap

[![Build Status](https://travis-ci.com/mgedmin/webtreemap-du.svg?branch=master)](https://travis-ci.com/mgedmin/webtreemap-du)

There are plenty of graphical tools to do this (e.g. Baobab, KFileLight),
but they are typically slow and/or inconvenient (consider a GUI-less server).
I often find myself running du on the command line (over ssh) and wishing
for something more visual.

Enter du2webtreemap!

    ssh someserver du /path/to/somewhere > du.txt
    du2webtreemap --html < du.txt > du.html
    xdg-open ./du.html

Or run ./demo.sh to see something quick and local.

These days I mostly webtreemap-du this via
https://github.com/ProgrammersOfVilnius/pov-server-page rather than directly.

This is based on webtreemap (https://github.com/martine/webtreemap), which was
conveniently imported as a git subtree via

    git subtree add --prefix=webtreemap https://github.com/martine/webtreemap v1

Note: webtreemap master is a full rewrite with a different API and a divergent
commit history.  Updating to use it will be fun!
