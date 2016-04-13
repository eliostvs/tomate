from __future__ import unicode_literals

import unittest

from mock import Mock
from wiring import FactoryProvider, SingletonScope

from tomate.constant import State
from tomate.event import on
from tomate.plugin import Plugin


class TestPlugin(unittest.TestCase):

    def setUp(self):
        session = Mock()
        timer = Mock()

        class Foo(Plugin):
            @on(session, [State.finished])
            def bar(self, sender):
                return sender

            @on(timer, [State.finished, State.changed])
            def spam(self, sender):
                return sender

        self.foo = Foo()
        self.timer_event = timer
        self.session_event = session

    def test_should_disconnect_events_when_plugin_deactive(self):
        self.foo.deactivate()

        self.timer_event.disconnect.assert_any_call(self.foo.spam, sender=State.changed)
        self.timer_event.disconnect.assert_any_call(self.foo.spam, sender=State.finished)

    def test_should_connect_events_when_plugin_active(self):
        self.foo.activate()

        self.timer_event.connect.assert_any_call(self.foo.spam, sender=State.changed, weak=False)
        self.timer_event.connect.assert_any_call(self.foo.spam, sender=State.finished, weak=False)


class TestPluginModule(unittest.TestCase):

    def test_module(self):
        from yapsy.PluginManagerDecorator import PluginManagerDecorator
        from tomate.plugin import PluginModule
        from tomate.graph import graph

        PluginModule().add_to(graph)

        provider = graph.providers['tomate.plugin']
        self.assertIn('tomate.plugin', graph.providers.keys())

        self.assertIsInstance(provider, FactoryProvider)
        self.assertEqual(provider.scope, SingletonScope)
        self.assertEqual(provider.dependencies, {})

        plugin_manager = graph.get('tomate.plugin')
        self.assertIsInstance(plugin_manager, PluginManagerDecorator)
