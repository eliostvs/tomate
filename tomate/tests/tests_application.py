from __future__ import unicode_literals

import unittest

from mock import Mock, patch


@patch('tomate.application.dbus.SessionBus')
class ApplicationFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.application_class = Mock()
        self.application_class.BUS_NAME = 'bus_name'
        self.application_class.BUS_OBJECT_PATH = 'bus_object_path'
        self.application_class.BUS_INTERFACE_NAME = 'bus_interface_name'
        self.view_class = Mock()

    def test_bus_request_name(self, mSessionBus):
        import dbus.bus
        from tomate.application import application_factory

        application_factory(self.application_class, self.view_class)

        self.assertTrue(mSessionBus.called)

        mSessionBus.return_value.request_name.assert_called_once_with(
            self.application_class.BUS_NAME,
            dbus.bus.NAME_FLAG_DO_NOT_QUEUE
        )

    def test_should_instantiate_the_application_class(self, mSessionBus):
        import dbus.bus
        from tomate.application import application_factory

        mSessionBus.return_value.request_name.return_value = dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER

        application_factory(self.application_class, self.view_class)

        self.application_class.assert_called_once_with(mSessionBus.return_value,
                                                       view=self.view_class)

    @patch('tomate.application.dbus.Interface')
    def test_should_get_bus_object(self, mInterface, mSessionBus):
        import dbus.bus
        from tomate.application import application_factory

        mSessionBus.return_value.request_name.return_value = dbus.bus.REQUEST_NAME_REPLY_EXISTS

        application_factory(self.application_class, self.view_class)

        mSessionBus.return_value.get_object.assert_called_once_with(
            'bus_name', 'bus_object_path'
        )

        mInterface.assert_called_once_with(mSessionBus.return_value.get_object.return_value,
                                           'bus_interface_name')


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.application import BaseApplication

        self.view = Mock()
        self.app = BaseApplication(Mock(), self.view)
        self.app.pomodoro = Mock()

    def test_application_start_for_the_first_time(self):
        self.app.start()

        self.view.run_window.assert_called_once_with()
        self.app.pomodoro.change_task.assert_called_once_with()

    def test_application_start_when_another_instance_is_running(self):
        self.app.running = True

        self.app.start()

        self.view.show_window.assert_called_once_with()

    def test_application_exit_when_pomodoro_is_running(self):
        self.app.pomodoro.state = 'running'

        self.assertEqual(False, self.app.exit())
        self.view.hide_window.assert_called_once_with()

    def test_application_exit_when_pomodoro_is_not_running(self):
        self.app.pomodoro.state = 'stopped'

        self.assertEqual(True, self.app.exit())
        self.view.delete_window.assert_called_once_with()

    def test_application_is_running_method(self):
        self.assertEqual(False, self.app.is_running())

        self.app.running = True

        self.assertEqual(True, self.app.is_running())
