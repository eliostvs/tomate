from __future__ import unicode_literals

import unittest

import dbus
from mock import Mock, patch
from tomate.enums import State
from wiring import Graph


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.app import Application

        self.app = Application(Mock(),
                               view=Mock(),
                               config=Mock(),
                               plugin=Mock())

    def test_interface(self, *args):
        from tomate.app import IApplication

        IApplication.check_compliance(self.app)

    @patch('tomate.app.dbus.SessionBus')
    def test_factory(self, *args):
        from tomate.app import Application

        graph = Graph()
        graph.register_factory('tomate.view', Mock)
        graph.register_factory('tomate.config', Mock)
        graph.register_factory('tomate.plugin', Mock)

        graph.register_factory('tomate.app', Application)

        app = Application.fromgraph(graph)
        self.assertIsInstance(app, Application)

        with patch('tomate.app.dbus.SessionBus.return_value.request_name',
                   return_value=dbus.bus.REQUEST_NAME_REPLY_EXISTS):
            dbus_app = Application.fromgraph(graph)
            self.assertIsInstance(dbus_app, dbus.Interface)

    def test_run_when_not_running(self):
        self.app.run()
        self.app.view.run.assert_called_once_with()

    def test_run_when_already_running(self):
        self.app.state = State.running
        self.app.run()

        self.app.view.show.assert_called_once_with()

    def test_is_running(self):
        self.assertEqual(False, self.app.is_running())

        self.app.state = State.running

        self.assertEqual(True, self.app.is_running())
