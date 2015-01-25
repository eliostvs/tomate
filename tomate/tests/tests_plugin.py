from __future__ import unicode_literals

import unittest

from mock import Mock, patch


class TomatePluginTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.plugin import TomatePlugin

        class Dummy(TomatePlugin):
            pass

        self.dummy = Dummy()

    @patch('tomate.plugin.ConnectSignalMixin.disconnect_signals')
    def test_deactivate_plugin(self, mdisconnect_signals):
        self.dummy.deactivate()

        mdisconnect_signals.assert_called_once_with()

    @patch('tomate.plugin.ConnectSignalMixin.connect_signals')
    def test_activate_plugin(self, mconnect_signals):
        self.dummy.activate()

        mconnect_signals.assert_called_once_with()

    @patch('tomate.plugin.TomatePlugin.initialize')
    def test_intialize_plugin(self, minitialize):
        from tomate.plugin import TomatePlugin

        class dummy(TomatePlugin):
            pass

        dummy()

        minitialize.assert_called_once_with()


class AddViewPluginManagerDecoratorTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_view = Mock(name='View')

    def test_should_set_view_property_on_init(self):
        from tomate.plugin import AddViewPluginManager

        pm = AddViewPluginManager(view=self.mock_view)

        self.assertEqual(self.mock_view, pm._view)

    def test_set_view_property_by_setView(self):
        from tomate.plugin import AddViewPluginManager

        pm = AddViewPluginManager()

        self.assertEqual(None, pm._view)

        pm.setView(self.mock_view)

        self.assertEqual(self.mock_view, pm._view)

    def test_should_add_view_instance_to_all_plugins(self):
        from tomate.plugin import AddViewPluginManager

        plugin = Mock(name='plugin')
        pm = AddViewPluginManager(view=self.mock_view)
        pm._component = Mock()
        pm._component.loadPlugins.return_value = [plugin]
        pm.loadPlugins()

        self.assertEqual(self.mock_view, plugin.plugin_object.view)
