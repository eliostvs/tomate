from __future__ import unicode_literals

import pytest

from blinker import Namespace
from mock import Mock
from wiring import Graph, InstanceProvider

from tomate.constant import State
from tomate.event import (on, EventModule, Subscriber, SubscriberMeta, Dispatcher,
                          methods_with_events, disconnect_events)


@pytest.fixture()
def session():
    return Mock()


@pytest.fixture()
def timer():
    return Mock()


@pytest.fixture()
def foo(session, timer):

    class Foo(object):
        @on(session, [State.finished])
        def bar(self, sender):
            return sender

        @on(timer, [State.finished, State.changed])
        def spam(self, sender):
            return sender

    return Foo()


def test_should_return_events_and_states_bind_with_the_method(foo, session, timer):
    assert foo.bar._events == [(session, State.finished)]

    assert foo.spam._events == [(timer, State.finished), (timer, State.changed)]


def test_should_return_methods_that_has_events(foo):
    SubscriberMeta(str('name'), (object,), {})

    assert  [foo.bar, foo.spam] ==  methods_with_events(foo)


def test_should_connect_event_with_the_method(session, timer):
    class Baz(Subscriber):
        @on(session, [State.finished])
        @on(timer, [State.changed])
        def bar(self, sender):
            return sender

    baz = Baz()

    session.connect.assert_called_with(baz.bar, sender=State.finished, weak=False)
    timer.connect.assert_called_with(baz.bar, sender=State.changed, weak=False)


def test_should_disconnect_bind_events(session, timer, foo):
    disconnect_events(foo)

    session.disconnect.assert_called_with(foo.bar, sender=State.finished)

    timer.disconnect.assert_any_call(foo.spam, sender=State.changed)
    timer.disconnect.assert_any_call(foo.spam, sender=State.finished)


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.fixture()
def event(dispatcher):
    return dispatcher.signal('event')


class TestDispatcher:

    def test_should_return_event_by_key(self, dispatcher, event):
        assert event == dispatcher['event']

    def test_should_return_event_by_attribute(self, dispatcher, event):
        assert event == dispatcher.event

    def test_should_return_a_empty_list(self, dispatcher):
        assert dispatcher.__bases__ == []


def test_event_module():
    graph = Graph()

    assert ['tomate.events'] == EventModule.providers.keys()

    EventModule().add_to(graph)

    provider = graph.providers['tomate.events']

    assert isinstance(provider, InstanceProvider)
    assert provider.scope is None
    assert provider.dependencies == {}

    assert isinstance(graph.get('tomate.events'), Namespace)
