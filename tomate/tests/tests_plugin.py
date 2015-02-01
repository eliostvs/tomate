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
    def test_deactivate_plugin(self, mock_disconnect):
        self.assertEqual(None, self.dummy.on_deactivate())

        self.dummy.on_deactivate = Mock('on_deactivate')
        self.dummy.deactivate()

        mock_disconnect.assert_called_once_with()
        self.dummy.on_deactivate.assert_called_once_with()

    @patch('tomate.plugin.ConnectSignalMixin.connect_signals')
    def test_activate_plugin(self, mock_connect):
        self.assertEqual(None, self.dummy.on_activate())

        self.dummy.on_activate = Mock('on_activate')
        self.dummy.activate()

        mock_connect.assert_called_once_with()
        self.dummy.on_activate.assert_called_once_with()

    @patch('tomate.plugin.TomatePlugin.on_init')
    def test_intialize_plugin(self, mock_init):
        from tomate.plugin import TomatePlugin

        class Dummy(TomatePlugin):
            pass

        Dummy()

        mock_init.assert_called_once_with()


class AddViewPluginManagerDecoratorTestCase(unittest.TestCase):

    def test_should_set_view_property_on_init(self):
        from tomate.plugin import TomatePluginManager

        app = Mock()
        pm = TomatePluginManager(application=app)

        self.assertEqual(app, pm._application)

    def test_set_view_property_by_setApplication(self):
        from tomate.plugin import TomatePluginManager

        pm = TomatePluginManager()
        app = Mock()

        self.assertEqual(None, pm._application)

        pm.setApplication(app)

        self.assertEqual(app, pm._application)

    def test_should_add_view_instance_to_all_plugins(self):
        from tomate.plugin import TomatePluginManager

        plugin = Mock(name='plugin')
        app = Mock()
        pm = TomatePluginManager(application=app)
        pm._component = Mock()
        pm._component.loadPlugins.return_value = [plugin]
        pm.loadPlugins()

        self.assertEqual(app, plugin.plugin_object.application)
