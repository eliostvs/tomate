import pytest
from mock import Mock

from tomate.event import ObservableProperty


class Foo(object):
    function = Mock()

    state = ObservableProperty('a', function, event='spam')
    other_state = ObservableProperty('b', function, '_hide')


@pytest.fixture()
def foo():
    return Foo()


def test_should_return_initial_value(foo):
    assert 'a' == foo.state
    assert 'a' == Foo.state


def test_should_has_default_attribute(foo):
    foo.state = 'a'

    assert hasattr(foo, '_state')
    assert 'a' == foo.state


def test_should_has_configurable_attribute(foo):
    foo.other_state = 'b'

    assert hasattr(foo, '_hide')
    assert foo.other_state == foo._hide


def test_should_call_trigger_method_with_choosed_event_type(foo):
    foo.state = 'a'

    foo.function.assert_called_with(foo, 'spam')


def test_should_call_trigger_method_with_default_event_type(foo):
    foo.other_state = 'b'

    foo.function.assert_called_with(foo, 'b')
