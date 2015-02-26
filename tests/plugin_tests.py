from __future__ import unicode_literals

import unittest

from mock import Mock, patch
from wiring import FactoryProvider, SingletonScope


class TestPlugin(unittest.TestCase):

    @patch('tomate.plugin.ConnectSignalMixin.disconnect_signals')
    @patch('tomate.plugin.ConnectSignalMixin.connect_signals')
    def test_interface(self, connect, disconnect):
        from tomate.plugin import Plugin
        from yapsy.IPlugin import IPlugin

        class Dummy(Plugin):
            pass

        dummy = Dummy()

        self.assertIsInstance(dummy, IPlugin)

        dummy.activate()
        connect.assert_called_once_with()

        dummy.deactivate()
        disconnect.assert_called_once_with()


class TestInjectablePluginManager(unittest.TestCase):

    def test_plugin_manager(self):
        from tomate.plugin import InjectablePluginManager
        from tomate.graph import graph

        plugin = Mock()
        manager = InjectablePluginManager()
        manager.setGraph(graph)
        manager._component = Mock(**{'loadPlugins.return_value': [plugin]})
        manager.loadPlugins()

        self.assertEqual(graph, plugin.plugin_object.graph)


class TestProviderModule(unittest.TestCase):

    def test_module(self):
        from tomate.plugin import PluginProvider
        from tomate.graph import graph
        from yapsy.PluginManagerDecorator import PluginManagerDecorator

        PluginProvider().add_to(graph)

        provider = graph.providers['tomate.plugin']
        self.assertEqual(['tomate.plugin'], graph.providers.keys())

        self.assertIsInstance(provider, FactoryProvider)
        self.assertEqual(provider.scope, SingletonScope)
        self.assertEqual(provider.dependencies, {})

        plugin_manager = graph.get('tomate.plugin')
        self.assertIsInstance(plugin_manager, PluginManagerDecorator)

        self.assertEqual(plugin_manager._graph, graph)
