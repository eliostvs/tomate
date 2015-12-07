from __future__ import unicode_literals

import unittest

from mock import patch
from wiring import FactoryProvider, SingletonScope


class TestProviderModule(unittest.TestCase):

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
