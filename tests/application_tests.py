from __future__ import unicode_literals

import unittest

import dbus
from mock import Mock
from tomate.enums import State
from wiring import Graph


class TestApplicationInterface(unittest.TestCase):

    def test_interface(self, *args):
        from tomate.application import IApplication, Application

        app = Application(config=Mock(), plugin=Mock(), bus=Mock())

        IApplication.check_compliance(app)


class TestApplicationFactory(unittest.TestCase):

    def test_factory(self):
        from tomate.application import Application, application_factory

        bus_session = Mock()
        graph = Graph()
        graph.register_instance('bus.session', bus_session)
        graph.register_factory('tomate.view', Mock)
        graph.register_factory('tomate.config', Mock)
        graph.register_factory('tomate.plugin', Mock)

        graph.register_factory('tomate.app', Application)

        app = application_factory(graph)
        self.assertIsInstance(app, Application)

        bus_session.request_name.return_value = dbus.bus.REQUEST_NAME_REPLY_EXISTS
        dbus_app = application_factory(graph)
        self.assertIsInstance(dbus_app, dbus.Interface)


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.application import Application

        self.app = Application(view=Mock(),
                               bus=Mock(),
                               config=Mock(),
                               plugin=Mock())

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
