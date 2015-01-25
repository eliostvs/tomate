from __future__ import unicode_literals

import unittest

from mock import Mock, patch


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

        application_factory(self.application_class)

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

        application_factory(self.application_class)

        mSessionBus.return_value.get_object.assert_called_once_with(
            'bus_name', 'bus_object_path'
        )

        mInterface.assert_called_once_with(mSessionBus.return_value.get_object.return_value,
                                           'bus_interface_name')


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.application import Application

        self.app = Application(Mock(name='dbus'))
        self.app.pomodoro = Mock(name='pomodoro')
        self.app.view = Mock(name='view')

    def test_application_start_for_the_first_time(self):
        self.app.start()

        self.app.view.run_window.assert_called_once_with()
        self.app.pomodoro.change_task.assert_called_once_with()

    def test_application_start_when_another_instance_is_running(self):
        self.app.running = True
        self.app.start()

        self.app.view.show_window.assert_called_once_with()

    def test_application_exit_when_pomodoro_is_running(self):
        self.app.pomodoro.state = 'running'

        self.assertEqual(False, self.app.exit())
        self.app.view.hide_window.assert_called_once_with()

    def test_application_exit_when_pomodoro_is_not_running(self):
        self.app.pomodoro.state = 'stopped'

        self.assertEqual(True, self.app.exit())
        self.app.view.delete_window.assert_called_once_with()

    def test_application_is_running_method(self):
        self.assertEqual(False, self.app.is_running())

        self.app.running = True

        self.assertEqual(True, self.app.is_running())

    def test_should_instantiate_iview_class(self):
        from tomate.application import Application
        from tomate.view import IView

        app = Application(Mock())

        self.assertIsInstance(app.view, IView)

    def test_initialize_with_a_custom_class(self):
        from tomate.application import Application

        class Dummy(Application):
            view_class = Mock

        app = Dummy(Mock())

        self.assertIsInstance(app.view, Mock)
