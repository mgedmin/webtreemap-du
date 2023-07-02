import json
import sys
from io import StringIO

import pytest

import du2webtreemap as dw


@pytest.mark.parametrize('size, expected', [
    (0, '0.0 KiB'),
    (1, '1.0 KiB'),
    (1024, '1.0 MiB'),
    (1500, '1.5 MiB'),
    (1024**2, '1.0 GiB'),
    (1024**3, '1.0 TiB'),
])
def test_fmt_size(size, expected):
    assert dw.fmt_size(size) == expected


def test_TreeNode_empty():
    node = dw.TreeNode()
    assert node.as_json('/foo') == {
        "name": "/foo",
        "data": {
            "$area": 0,
        },
        "children": [],
    }


def test_TreeNode_with_size():
    node = dw.TreeNode()
    node.size = 2048
    assert node.as_json('/foo') == {
        "name": "/foo 2.0 MiB",
        "data": {
            "$area": 2048,
        },
        "children": [],
    }


def test_TreeNode_with_children():
    node = dw.TreeNode()
    node.children['bar'].size = 2048
    node.children['baz'].size = 1024
    assert node.as_json('/foo') == {
        # Note: size not shown since we never set node.size
        "name": "/foo",
        "data": {"$area": 3072},
        "children": [
            # Note: children sorted by size (largest first), then
            # alphabetically
            {
                "name": "bar 2.0 MiB",
                "data": {"$area": 2048},
                "children": [],
            },
            {
                "name": "baz 1.0 MiB",
                "data": {"$area": 1024},
                "children": [],
            },
        ],
    }


def test_parse_du():
    root = dw.parse_du([
        '11 ./foo/a\n',
        '42 ./foo\n',
        '17 ./bar\n',
        '63 .\n',
    ])
    assert root.get_size() == 63
    assert sorted(root.children) == ['.']
    assert sorted(root.children['.'].children) == ['bar', 'foo']
    assert sorted(root.children['.'].children['foo'].children) == ['a']


def test_parse_root_relative():
    root = dw.parse_du([
        '11 /foo/a\n',
        '42 /foo\n',
        '17 /bar\n',
        '63 /\n',
    ])
    assert root.get_size() == 63
    # TBH I'm not sure this is right; maybe I should insist on /
    assert sorted(root.children) == ['']
    assert sorted(root.children[''].children) == ['bar', 'foo']
    assert sorted(root.children[''].children['foo'].children) == ['a']


@pytest.mark.parametrize('input', [
    ['this-is-not-du-output\n'],
    ['this is not du output\n'],
    ['42 here\n', '43 there\n', '5 here\n'],
])
def test_parse_du_errors(input):
    with pytest.raises(dw.InputSyntaxError):
        dw.parse_du(input)


def test_main_help(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap', '--help'])
    with pytest.raises(SystemExit):
        dw.main()


def test_main_help_when_no_args_and_a_tty(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap'])
    monkeypatch.setattr(sys.stdin, 'isatty', lambda: True)
    with pytest.raises(SystemExit):
        dw.main()


def test_main(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap'])
    monkeypatch.setattr(sys, 'stdin', StringIO("42 foo\n"))
    dw.main()
    output = capsys.readouterr().out
    assert output.startswith('var tree = {')
    assert output.endswith('};\n')
    assert output.count('\n') == 1
    assert json.loads(output[11:-2]) == {
        "name": "foo 42.0 KiB",
        "data": {"$area": 42},
        "children": [],
    }


def test_main_pretty_print(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap', '-p'])
    monkeypatch.setattr(sys, 'stdin', StringIO("42 foo\n"))
    dw.main()
    output = capsys.readouterr().out
    assert output.startswith('var tree = {')
    assert output.endswith('};\n')
    assert output.count('\n') == 7
    assert json.loads(output[11:-2]) == {
        "name": "foo 42.0 KiB",
        "data": {"$area": 42},
        "children": [],
    }


def test_main_html(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap', '--html'])
    monkeypatch.setattr(sys, 'stdin', StringIO("42 foo\n"))
    dw.main()
    output = capsys.readouterr().out
    assert output.startswith('<!DOCTYPE')


def test_main_dot_name(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap', '-d', '/var'])
    monkeypatch.setattr(sys, 'stdin', StringIO("42 ./foo\n"))
    dw.main()
    output = capsys.readouterr().out
    assert output.startswith('var tree = {')
    assert output.endswith('};\n')
    assert json.loads(output[11:-2]) == {
        "name": "/var",
        "data": {"$area": 42},
        "children": [
            {
                "name": "foo 42.0 KiB",
                "data": {"$area": 42},
                "children": [],
            },
        ],
    }


def test_main_multiple_top_levels(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap'])
    monkeypatch.setattr(sys, 'stdin', StringIO("42 foo\n11 bar\n"))
    dw.main()
    output = capsys.readouterr().out
    assert output.startswith('var tree = {')
    assert output.endswith('};\n')
    assert json.loads(output[11:-2]) == {
        "name": "total disk usage 53.0 KiB",
        "data": {"$area": 53},
        "children": [
            {
                "name": "foo 42.0 KiB",
                "data": {"$area": 42},
                "children": [],
            },
            {
                "name": "bar 11.0 KiB",
                "data": {"$area": 11},
                "children": [],
            },
        ],
    }


def test_main_nonascii(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['du2webtreemap'])
    monkeypatch.setattr(sys, 'stdin', StringIO("42 fø\n"))
    dw.main()
    output = capsys.readouterr().out
    assert output.startswith('var tree = {')
    assert output.endswith('};\n')
    assert output.count('\n') == 1
    assert json.loads(output[11:-2]) == {
        "name": u"fø 42.0 KiB",
        "data": {"$area": 42},
        "children": [],
    }
