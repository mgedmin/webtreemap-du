#!/usr/bin/python
"""
Convert disk usage numbers produced by 'du' to webtreemap data suitable for
https://github.com/martine/webtreemap

Usage: du /path | du2webtreemap.py > du.js
"""

import sys
import json
import fileinput
from collections import defaultdict


def fmt_size(kb):
    units = 'KiB'
    for units in 'KiB', 'MiB', 'GiB', 'TiB':
        if kb < 1024:
            break
        kb /= 1024.0
    return '%.0f %s' % (kb, units)


class TreeNode(object):

    def __init__(self):
        self.size = None
        self.children = defaultdict(TreeNode)

    def as_json(self, name):
        return dict(
            name='%s %s' % (name, fmt_size(self.size)) if self.size is not None
                 else name,
            data={
                "$area": self.size if self.size is not None
                         else sum(child.size
                                  for child in self.children.values()),
            },
            children=[
                child.as_json(name or "/")
                for name, child in sorted(self.children.items())
            ],
        )


class InputSyntaxError(Exception):
    """Input data does not conform to the expected format."""


def parse_du(input):
    """Parse a sequence of lines from 'du'.

    Input format: a sequence of lines; each line has a numerical size
    (kilobytes, but we don't care, as long as the units are the same),
    some whitespace, and the directory name.  Subdirectories appear before
    parent directories.
    """
    root = TreeNode()
    for line in input:
        # Tokenize
        try:
            size, filename = line.split(None, 1)
        except ValueError:
            raise InputSyntaxError('could not parse %r' % line)
        try:
            size = int(size)
        except ValueError:
            raise InputSyntaxError('size is not a number: %r' % size)
        filename = filename.rstrip()
        # Process
        node = root
        for part in filename.split('/'):
            node = node.children[part]
        if node.size is not None:
            raise InputSyntaxError('size of %s was already specified previously' % filename)
        node.size = size
    return root


def main():
    if len(sys.argv) == 1 and sys.stdin.isatty() or '--help' in sys.argv:
        sys.exit(__doc__)
    tree = parse_du(fileinput.input())
    sys.stdout.write("var tree = ")
    json.dump(tree.as_json('disk usage (kilobytes)'), sys.stdout, indent=2)


if __name__ == '__main__':
    main()
