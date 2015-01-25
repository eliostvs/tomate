from __future__ import unicode_literals

import unittest

from mock import Mock, patch


class TomatePluginTestCase(unittest.TestCase):

    @patch('tomate.plugin.ConnectSignalMixin.disconnect_signals')
    @patch('tomate.plugin.ConnectSignalMixin.connect_signals')
    def test_plugin_inherit(self, mconnect_signals, mdisconnect_signals):
        from yapsy.IPlugin import IPlugin
        from tomate.plugin import TomatePlugin
        from tomate.base import ConnectSignalMixin

        class Dummy(TomatePlugin):
            pass

        dummy = Dummy()

        self.assertIsInstance(dummy, IPlugin)
        self.assertIsInstance(dummy, ConnectSignalMixin)

        dummy.activate()
        mconnect_signals.assert_called_once_with()

        dummy.deactivate()
        mdisconnect_signals.assert_called_once_with()


class AddViewInstancePluginManagerDecoratorTestCase(unittest.TestCase):

    def test_should_add_view_instance_to_all_plugins(self):
        from tomate.plugin import AddViewInstancePluginManager

        view = Mock(name='View')
        plugin = Mock(name='plugin')
        pm = AddViewInstancePluginManager()
        pm.setViewInstance(view)

        self.assertEqual(view, pm.view_instance)

        pm._component = Mock()
        pm._component.loadPlugins.return_value = [plugin]
        pm.loadPlugins()

        self.assertEqual(view, plugin.plugin_object.view)
