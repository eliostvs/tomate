from __future__ import unicode_literals

import unittest

from mock import Mock, patch
from tomate.enums import State


class TestApplicationInterface(unittest.TestCase):

    def test_interface(self):
        from tomate.application import IApplication, Application

        app = Application()
        IApplication.check_compliance(app)


@patch('tomate.application.dbus.SessionBus')
class ApplicationFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.application_class = Mock()
        self.application_class.bus_name = 'bus_name'
        self.application_class.bus_object_path = 'bus_object_path'
        self.application_class.bus_interface_name = 'bus_interface_name'

    def test_bus_request_name(self, mSessionBus):
        import dbus.bus
        from tomate.application import application_factory

        application_factory(self.application_class, Mock)

        self.assertTrue(mSessionBus.called)

        mSessionBus.return_value.request_name.assert_called_once_with(
            self.application_class.bus_name,
            dbus.bus.NAME_FLAG_DO_NOT_QUEUE
        )

    @patch('tomate.application.dbus.Interface')
    def test_should_get_bus_object(self, mInterface, mSessionBus):
        import dbus.bus
        from tomate.application import application_factory

        mSessionBus.return_value.request_name.return_value = dbus.bus.REQUEST_NAME_REPLY_EXISTS

        application_factory(self.application_class, Mock)

        mSessionBus.return_value.get_object.assert_called_once_with(
            'bus_name', 'bus_object_path'
        )

        mInterface.assert_called_once_with(mSessionBus.return_value.get_object.return_value,
                                           'bus_interface_name')


@patch('tomate.profile.ProfileManager.get_plugin_paths', spec_set=True, return_value=[])
class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.application import Application

        self.app = Application(Mock, Mock())

    def test_should_run_view_when_not_running(self, *args):
        self.app.run()

        self.app.view.run.assert_called_once_with()
        self.app.pomodoro.change_task.assert_called_once_with()

    def test_should_show_view_when_already_running(self, *args):
        self.app.state = State.running
        self.app.run()

        self.app.view.show.assert_called_once_with()

    def test_should_hide_view_when_pomodoro_is_running(self, *args):
        self.app.pomodoro.timer_is_running.return_value = True
        self.app.quit()

        self.app.view.hide.assert_called_once_with()

    def test_should_quit_when_pomodoro_is_not_running(self, *args):
        self.app.pomodoro.timer_is_running.return_value = False
        self.app.quit()

        self.app.view.quit.assert_called_once_with()

    def test_application_is_running_method(self, *args):
        self.assertEqual(False, self.app.is_running())

        self.app.running = True

        self.assertEqual(True, self.app.is_running())
