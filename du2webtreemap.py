#!/usr/bin/python3
"""
Convert disk usage numbers produced by 'du' to webtreemap data suitable for
https://github.com/martine/webtreemap

Usage: du /path | du2webtreemap.py > du.js
  or   du /path | du2webtreemap.py --html > du.html; firefox du.html
"""

import sys
import json
import optparse
import fileinput
from collections import defaultdict
from functools import partial


__author__ = 'Marius Gedminas <marius@gedmin.as>'
__version__ = '2.1.1'
__date__ = '2025-03-20'


def fmt_size(kb):
    units = 'KiB'
    for units in 'KiB', 'MiB', 'GiB', 'TiB':
        if kb < 1024:
            break
        kb /= 1024.0
    return '%.1f %s' % (kb, units)


class TreeNode(object):

    size = None
    _computed_size = None

    def __init__(self):
        self.children = defaultdict(TreeNode)

    def get_size(self):
        if self.size is not None:
            return self.size
        if self._computed_size is None:
            self._computed_size = sum(child.get_size()
                                      for child in self.children.values())
        return self._computed_size

    def as_json(self, name):
        return dict(
            name='%s %s' % (name, fmt_size(self.size)) if self.size is not None
                 else name,
            data={
                "$area": self.get_size(),
            },
            children=[
                child.as_json(name or "/")
                for name, child in sorted(
                    self.children.items(),
                    key=lambda nc: (-nc[1].get_size(), nc[0]))
            ],
        )


class InputSyntaxError(Exception):
    """Input data does not conform to the expected format."""


def parse_du(input):
    """Parse a sequence of lines from 'du'.

    Input format: a sequence of lines (as byte strings); each line has a
    numerical size (kilobytes, but we don't care, as long as the units are the
    same), some whitespace, and the directory name.  Subdirectories appear
    before parent directories.
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
        filename = filename.decode('UTF-8', 'replace')
        filename = filename.rstrip('\r\n/')
        # Process
        node = root
        for part in filename.split('/'):
            node = node.children[part]
        if node.size is not None:
            raise InputSyntaxError(
                'size of %s was already specified previously' % filename)
        node.size = size
    return root


HTML_TEMPLATE = """\
<!DOCTYPE HTML>
<html>
  <head>
    <title>Disk Usage</title>
    <link rel="stylesheet" href="webtreemap/webtreemap.css" />
    <style>
      body {
        font-family: sans-serif;
        font-size: 0.8em;
        margin: 2ex 4ex;
      }

      h1 {
        font-weight: normal;
      }

      #map {
        width: 800px;
        height: 480px;
        position: relative;
        cursor: pointer;
        -webkit-user-select: none;
      }
    </style>
  </head>
  <body>
    <h1>Disk Usage</h1>
    <p>Click on a box to zoom in.  Click on the outermost box to zoom out.</p>
    <div id="map"></div>
    <script src="webtreemap/webtreemap.js"></script>
    <script>
      %(data)s
      var map = document.getElementById('map');
      appendTreemap(map, tree);
    </script>
  </body>
</html>
"""


def main():
    parser = optparse.OptionParser(
        usage='%prog [options] < input.txt > output.js\n'
              '       %prog --html [options] < input.txt > output.html')
    parser.add_option('-p', '--pretty-print', action='store_true',
                      help='pretty-print the output')
    parser.add_option('-d', '--dot-name', metavar='NEWNAME',
                      help='rename the root node, if it is "."')
    parser.add_option('--html', action='store_true',
                      help='output HTML with embedded JSON')
    opts, args = parser.parse_args()
    if not args and sys.stdin.isatty():
        parser.print_help()
        sys.exit(0)
    tree = parse_du(fileinput.input(args, mode='rb'))
    if opts.dot_name and list(tree.children) == ['.']:
        tree.children = {opts.dot_name: tree.children['.']}

    if len(tree.children) == 1:
        [(name, root)] = tree.children.items()
        json_data = root.as_json(name or '/')
    else:
        json_data = tree.as_json('total disk usage %s'
                                 % fmt_size(tree.get_size()))

    if opts.pretty_print:
        format_json = partial(json.dumps, indent=2, sort_keys=True,
                              separators=(',', ': '))
    else:
        format_json = json.dumps

    data = "var tree = %s;" % format_json(json_data)
    if opts.html:
        print(HTML_TEMPLATE % dict(data=data))
    else:
        print(data)


if __name__ == '__main__':
    main()
