from __future__ import unicode_literals

import unittest

import six
from blinker import Namespace
from mock import Mock
from tomate.constant import State
from tomate.event import Events, on, EventsModule, Subscriber, SubscriberMeta, Dispatcher
from wiring import Graph, InstanceProvider


class Foo(object):
    @on(Events.Timer, [State.finished])
    def func(self, sender):
        return sender

    @on(Events.Timer, [State.finished, State.changed])
    def spam(self, sender):
        return sender


class Base(unittest.TestCase):
    def setUp(self):
        self.foo = Foo()


class DecoratorOnTest(Base):
    def test_should_return_events_bind_with_the_method(self):
        self.assertListEqual(self.foo.func._events, [(Events.Timer, State.finished)])

        self.assertListEqual(self.foo.spam._events,
                             [(Events.Timer, State.finished), (Events.Timer, State.changed)])


class SubscriberMetaTest(Base):
    def test_should_return_methods_that_has_events(self):
        meta = SubscriberMeta(str('name'), (object,), {})

        expected = [self.foo.func, self.foo.spam]
        self.assertEqual(expected, meta._SubscriberMeta__get_methods_with_events(self.foo))


class SubscriberTest(unittest.TestCase):
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


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.dispacther = Dispatcher()
        self.new_event = self.dispacther.signal('event')

    def test_should_return_event_by_key(self):
        self.assertEqual(self.new_event, self.dispacther['event'])

    def test_should_return_event_by_attribute(self):
        self.assertEqual(self.new_event, self.dispacther.event)


class EventsModuleTest(unittest.TestCase):

    def test_module(self):
        graph = Graph()

        six.assertCountEqual(self, ['tomate.events'], EventsModule.providers.keys())

        EventsModule().add_to(graph)

        provider = graph.providers['tomate.events']

        self.assertIsInstance(provider, InstanceProvider)
        self.assertEqual(provider.scope, None)
        self.assertEqual(provider.dependencies, {})

        self.assertIsInstance(graph.get('tomate.events'), Namespace)

if __name__ == '__main__':
    unittest.main()
