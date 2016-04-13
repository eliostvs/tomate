from __future__ import unicode_literals

import pytest

from tomate.utils import format_time_left, suppress_errors


@pytest.mark.parametrize('seconds, time_formated', [
    (25 * 60, '25:00'),
    (15 * 60, '15:00'),
    (5 * 60, '05:00'),
])
def test_format_seconds_in_string_with_minutes_and_seconds(seconds, time_formated):
    assert time_formated == format_time_left(seconds)


def test_not_raise_exception_when_block_has_decorator_supress_errors():
    exception = Exception('error')

    @suppress_errors
    def raise_exception():
        raise exception

    assert not raise_exception()
