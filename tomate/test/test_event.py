from __future__ import unicode_literals

import unittest

import six
from blinker import Namespace
from mock import Mock
from wiring import Graph, InstanceProvider

from tomate.constant import State
from tomate.event import (on, EventModule, Subscriber, SubscriberMeta, Dispatcher,
                          methods_with_events, disconnect_events)


class Base(unittest.TestCase):
    def setUp(self):
        Session = Mock()
        Timer = Mock()

        class Foo(object):
            @on(Session, [State.finished])
            def bar(self, sender):
                return sender

            @on(Timer, [State.finished, State.changed])
            def spam(self, sender):
                return sender

        self.foo = Foo()
        self.timer_event = Timer
        self.session_event = Session


class DecoratorOnTest(Base):
    def test_should_return_events_and_states_bind_with_the_method(self):
        self.assertListEqual(self.foo.bar._events, [(self.session_event, State.finished)])

        self.assertListEqual(self.foo.spam._events,
                             [(self.timer_event, State.finished), (self.timer_event, State.changed)])


class SubscriberMetaTest(Base):
    def test_should_return_methods_that_has_events(self):
        SubscriberMeta(str('name'), (object,), {})

        expected = [self.foo.bar, self.foo.spam]

        self.assertEqual(expected, methods_with_events(self.foo))


class SubscriberTest(Base):

    def test_should_connect_event_with_the_method(self):
        Session = Mock()
        Timer = Mock()

        class Baz(Subscriber):
            @on(Session, [State.finished])
            @on(Timer, [State.changed])
            def bar(self, sender):
                return sender

        baz = Baz()

        Session.connect.assert_called_with(baz.bar, sender=State.finished, weak=False)
        Timer.connect.assert_called_with(baz.bar, sender=State.changed, weak=False)


class TestDisconnectFunction(Base):

    def test_should_disconnect_bind_events(self):
        disconnect_events(self.foo)

        self.session_event.disconnect.assert_called_with(self.foo.bar, sender=State.finished)

        self.timer_event.disconnect.assert_any_call(self.foo.spam, sender=State.changed)
        self.timer_event.disconnect.assert_any_call(self.foo.spam, sender=State.finished)


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.dispacther = Dispatcher()
        self.new_event = self.dispacther.signal('event')

    def test_should_return_event_by_key(self):
        self.assertEqual(self.new_event, self.dispacther['event'])

    def test_should_return_event_by_attribute(self):
        self.assertEqual(self.new_event, self.dispacther.event)

    def test_should_return_a_empty_list(self):
        self.assertEqual(self.dispacther.__bases__, [])


class EventsModuleTest(unittest.TestCase):

    def test_module(self):
        graph = Graph()

        six.assertCountEqual(self, ['tomate.events'], EventModule.providers.keys())

        EventModule().add_to(graph)

        provider = graph.providers['tomate.events']

        self.assertIsInstance(provider, InstanceProvider)
        self.assertEqual(provider.scope, None)
        self.assertEqual(provider.dependencies, {})

        self.assertIsInstance(graph.get('tomate.events'), Namespace)

if __name__ == '__main__':
    unittest.main()
