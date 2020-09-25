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
