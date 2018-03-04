import pytest
from mock import Mock

from tomate.constant import State
from tomate.event import (on, Subscriber, SubscriberMeta, methods_with_events, disconnect_events)


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

    assert [foo.bar, foo.spam] == methods_with_events(foo)


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


def should_raise_attribute_error_when_key_not_found_in_the_namespace():
    from tomate.event import Events

    with pytest.raises(AttributeError):
        Events.Foo


def test_should_events_be_acessiable_as_dictionary_and_attributes():
    import tomate.event as e

    assert e.Session == e.Events.Session
    assert e.Session == e.Events.Session


def test_module(graph):
    import tomate.event as e

    assert e.Events is graph.get('tomate.events')
    assert e.Events.Setting is graph.get('tomate.events.setting')
    assert e.Events.Session is graph.get('tomate.events.session')
    assert e.Events.Timer is graph.get('tomate.events.timer')
    assert e.Events.View is graph.get('tomate.events.view')
