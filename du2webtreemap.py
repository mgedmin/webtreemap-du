#!/usr/bin/python
"""
Convert disk usage numbers produced by 'du' to webtreemap data suitable for
https://github.com/martine/webtreemap

Usage: du /path | du2webtreemap.py > du.js
"""

import sys
import json
import optparse
import fileinput
from collections import defaultdict


def fmt_size(kb):
    units = 'KiB'
    for units in 'KiB', 'MiB', 'GiB', 'TiB':
        if kb < 1024:
            break
        kb /= 1024.0
    return '%.1f %s' % (kb, units)


class TreeNode(object):

    def __init__(self):
        self.size = None
        self.children = defaultdict(TreeNode)

    def get_size(self):
        if self.size is not None:
            return self.size
        else:
            return sum(child.get_size() for child in self.children.values())

    def as_json(self, name):
        return dict(
            name='%s %s' % (name, fmt_size(self.size)) if self.size is not None
                 else name,
            data={
                "$area": self.get_size(),
            },
            children=[
                child.as_json(name or "/")
                for name, child in sorted(self.children.items(),
                                          key=lambda (n, c): c.size,
                                          reverse=True)
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
    parser = optparse.OptionParser(
        usage='%prog [options] < input.txt > output.js')
    parser.add_option('-p', '--pretty-print', action='store_true', 
                      help='pretty-print the output')
    parser.add_option('-d', '--dot-name', metavar='NEWNAME',
                      help='rename the root node, if it is "."')
    opts, args = parser.parse_args()
    if not args and sys.stdin.isatty():
        parser.print_help()
        return
    tree = parse_du(fileinput.input(args))
    if opts.dot_name and list(tree.children) == ['.']:
        tree.children = {opts.dot_name: tree.children['.']}

    if len(tree.children) == 1:
        name, root = tree.children.items()[0]
        json_data = root.as_json(name or '/')
    else:
        json_data = tree.as_json('total disk usage %s'
                                 % fmt_size(tree.get_size()))

    sys.stdout.write("var tree = ")
    json.dump(json_data, sys.stdout,
              indent=2 if opts.pretty_print else 0)


if __name__ == '__main__':
    main()
