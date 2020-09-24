Visualize disk usage with webtreemap

There are plenty of graphical tools to do this (e.g. Baobab, KFileLight),
but they are typically slow and/or inconvenient (consider a GUI-less server).
I often find myself running du on the command line (over ssh) and wishing
for something more visual.

Enter du2webtreemap!

    ssh someserver du /path/to/somewhere > du.txt
    du2webtreemap --html < du.txt > du.html
    xdg-open ./du.html

Or run ./demo.sh to see something quick and local.

This is based on webtreemap (https://github.com/martine/webtreemap), which was
conveniently imported as a git subtree via

    git subtree add --prefix=webtreemap https://github.com/martine/webtreemap 7839cf91548943a16a75d0483cce0be839a281ab

I'm a bit new to git subtrees.  I think you can update with

    git subtree pull --prefix=webtreemap https://github.com/martine/webtreemap master

(but beware: newer commits of webtreemap don't have the webtreemap.js, you have to use webpack to generate it somehow)
