from __future__ import unicode_literals

import unittest

from blinker import Namespace
from mock import Mock
from wiring import Graph, InstanceProvider

from tomate.enums import State
from tomate.events import Events, on, Subscriber, EventsModule, SubscriberMeta, Dispatcher


class Foo(object):
    @on(Events.Timer, State.finished)
    def func(self, sender):
        return sender


class Base(unittest.TestCase):
    def setUp(self):
        self.foo = Foo()


class DecoratorOnTest(Base):
    def test_should_return_bind_event_in_method(self):
        self.assertEqual(self.foo.func._bind, (Events.Timer, State.finished))


class SubscriberMetaTest(Base):
    def test_should_return_bind_methods(self):
        meta = SubscriberMeta(str('name'), (object,), {})
        self.assertEqual([self.foo.func], meta._SubscriberMeta__get_binds(self.foo))


class SubscriberTest(unittest.TestCase):
    def test_should_connect_method_on_given_event(self):
        Event = Mock()

        class Foo(Subscriber):
            @on(Event, State.finished)
            def func(self, sender):
                return sender

        foo = Foo()

        Event.connect.assert_called_once_with(foo.func, sender=State.finished, weak=False)


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

        self.assertEqual(['tomate.events'], EventsModule.providers.keys())
        EventsModule().add_to(graph)

        provider = graph.providers['tomate.events']

        self.assertIsInstance(provider, InstanceProvider)
        self.assertEqual(provider.scope, None)
        self.assertEqual(provider.dependencies, {})

        self.assertIsInstance(graph.get('tomate.events'), Namespace)

if __name__ == '__main__':
    unittest.main()
