from unittest.mock import Mock

import pytest
from yapsy.PluginManagerDecorator import PluginManagerDecorator

from tomate.constant import State
from tomate.event import on
from tomate.plugin import Plugin


@pytest.fixture()
def timer():
    return Mock()


@pytest.fixture()
def session():
    return Mock()


@pytest.fixture()
def foo(timer, session):
    class Foo(Plugin):
        @on(session, [State.finished])
        def bar(self, sender):
            return sender

        @on(timer, [State.finished, State.changed])
        def spam(self, sender):
            return sender

    return Foo()


def test_should_disconnect_events_when_plugin_deactive(foo, timer):
    foo.deactivate()

    timer.disconnect.assert_any_call(foo.spam, sender=State.changed)
    timer.disconnect.assert_any_call(foo.spam, sender=State.finished)


def test_should_connect_events_when_plugin_active(foo, timer):
    foo.activate()

    timer.connect.assert_any_call(foo.spam, sender=State.changed, weak=False)
    timer.connect.assert_any_call(foo.spam, sender=State.finished, weak=False)


def test_module(graph):
    assert 'tomate.plugin' in graph.providers

    assert isinstance(graph.get('tomate.plugin'), PluginManagerDecorator)
