from __future__ import unicode_literals

import unittest

import six
from mock import Mock
from tomate.constant import State, Task
from tomate.session import Session, SessionModule
from wiring import FactoryProvider, Graph, SingletonScope


class SessionTest(unittest.TestCase):

    def setUp(self):
        self.session = Session(timer=Mock(),
                               config=Mock(**{'get_int.return_value': 25}),
                               events=Mock())

    def test_should_no_be_able_to_start_when_state_is_not_valid(self):
        self.session.state = State.started

        self.assertFalse(self.session.start())

    def test_should_be_able_to_start_when_state_is_valid(self):
        for state in (State.stopped, State.finished):
            self.session.state = state

            self.assertTrue(self.session.start())
            self.assertEqual(State.started, self.session.state)

    def test_shoud_not_be_able_to_stop_when_state_is_not_valid(self):
        self.session.state = State.stopped

        self.assertFalse(self.session.stop())

    def test_shoud_not_be_able_to_stop_when_state_is_valid_and_timer_is_not_running(self):
        self.session.timer.state = State.stopped
        self.session.state = State.stopped

        self.assertFalse(self.session.stop())

    def test_should_be_able_to_stop_when_state_is_valid(self):
        self.session.state = State.started
        self.session.timer.state = State.started

        self.assertTrue(self.session.stop())
        self.assertEqual(State.stopped, self.session.state)

    def test_should_no_be_able_to_reset_when_state_is_not_valid(self):
        self.session.state = State.started

        self.assertFalse(self.session.reset())

    def test_should_be_able_to_reset_whe_state_is_valid(self):
        for state in (State.stopped, State.finished):
            self.session.count = 10
            self.session.state = state

            self.assertTrue(self.session.reset())
            self.assertEqual(0, self.session.count)

    def test_should_not_be_able_to_end_when_state_is_not_valid(self):
        self.session.state = State.stopped

        self.assertFalse(self.session.end())

    def test_should_not_be_able_to_end_when_the_state_is_valid_and_timer_is_running(self):
        self.session.state = State.started
        self.session.timer.state = State.started

        self.assertFalse(self.session.end())

    def test_should_be_able_to_end_when_state_is_valid_and_timer_is_not_running(self):
        self.session.state = State.started
        self.session.timer.state = State.stopped

        self.assertTrue(self.session.end())
        self.assertEqual(State.finished, self.session.state)

    def test_shoud_not_be_able_to_change_task_when_state_is_not_valid(self):
        self.session.state = State.started

        self.assertFalse(self.session.change_task(task=None))

    def test_should_be_able_to_change_task_when_state_is_valid(self):
        for state in (State.stopped, State.finished):
            self.session.timer.state = state

            self.session.change_task(dict(task=Task.shortbreak))
            self.assertTrue(self.session.change_task(task=Task.shortbreak))
            self.assertEqual(Task.shortbreak, self.session.task)

    def test_should_change_task_to_short_break(self):
        self.session.timer.state = State.stopped
        self.session.task = Task.pomodoro
        self.session.state = State.started
        self.session.count = 0
        self.session.config.get_int.return_value = 4

        self.session.end()

        self.assertEqual(Task.shortbreak, self.session.task)

    def test_should_change_task_to_pomodoro(self):
        for task in (Task.longbreak, Task.shortbreak):
            self.session.task = task
            self.session.timer.state = State.stopped
            self.session.state = State.started

            self.session.end()

            self.assertEqual(Task.pomodoro, self.session.task)

    def test_should_change_task_to_long_break(self):
        self.session.state = State.started
        self.session.task = Task.pomodoro
        self.session.count = 3
        self.session.config.get_int.return_value = 4

        self.assertTrue(self.session.end())
        self.assertEqual(Task.longbreak, self.session.task)

    def test_session_status(self):
        self.session.count = 2
        self.session.task = Task.shortbreak
        self.session.state = State.started
        self.session.config.get_int.return_value = 5

        expected = dict(task=Task.shortbreak,
                        sessions=2,
                        state=State.started,
                        time_left=5 * 60)

        self.assertEqual(expected, self.session.status())

    def test_should_call_config(self):
        self.session.config.reset_mock()

        self.assertEqual(25 * 60, self.session.duration)
        self.session.config.get_int.assert_called_once_with('Timer', 'pomodoro_duration')

    def test_should_trigger_start_event_when_session_start(self):
        self.session.start()

        self.session.event.send.assert_called_once_with(State.started,
                                                        task=Task.pomodoro,
                                                        sessions=0,
                                                        state=State.started,
                                                        time_left=1500)

    def test_should_trigger_stop_event_when_session_stop(self):
        self.session.state = State.started
        self.session.timer.state = State.started
        self.session.stop()

        self.session.event.send.assert_called_with(State.stopped,
                                                   task=Task.pomodoro,
                                                   sessions=0,
                                                   state=State.stopped,
                                                   time_left=1500)

    def test_should_trigger_changed_event_when_session_reset(self):
        self.session.count = 2
        self.session.reset()

        self.session.event.send.assert_called_with(State.reset,
                                                   task=Task.pomodoro,
                                                   sessions=0,
                                                   state=State.stopped,
                                                   time_left=1500)

    def test_should_trigger_finished_event(self):
        self.session.state = State.started
        self.session.timer.State = State.stopped
        self.session.config.get_int.return_value = 5
        self.session.end()

        self.session.event.send.assert_called_with(State.finished,
                                                   task=Task.shortbreak,
                                                   sessions=1,
                                                   state=State.finished,
                                                   time_left=300)

    def test_should_trigger_changed_event_when_task_change(self):
        self.session.config.get_int.return_value = 15
        self.session.change_task(task=Task.longbreak)

        self.session.event.send.assert_called_with(State.changed,
                                                   task=Task.longbreak,
                                                   sessions=0,
                                                   state=State.stopped,
                                                   time_left=900)


class SessionModuleTest(unittest.TestCase):

    def test_module(self):
        graph = Graph()

        six.assertCountEqual(self, ['tomate.session'], SessionModule.providers.keys())

        SessionModule().add_to(graph)

        provider = graph.providers['tomate.session']

        self.assertIsInstance(provider, FactoryProvider)
        self.assertEqual(provider.scope, SingletonScope)
        self.assertEqual(provider.dependencies,
                         dict(events='tomate.events',
                              config='tomate.config',
                              timer='tomate.timer'))

        graph.register_instance('tomate.events', Mock())
        graph.register_instance('tomate.timer', Mock())
        graph.register_instance('tomate.config', Mock(**{'get_int.return_value': 25}))
        self.assertIsInstance(graph.get('tomate.session'), Session)
