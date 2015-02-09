from __future__ import unicode_literals

import unittest

from mock import patch

from tomate.constants import State, Task


class PomodoroTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.pomodoro import Pomodoro

        self.pomodoro = Pomodoro()

    def test_should_return_pomodoro_task_and_zero_sessions(self):
        self.assertEqual(Task.pomodoro, self.pomodoro.task)
        self.assertEqual(0, self.pomodoro.sessions)

    def test_pomodoro_states(self):
        self.assertEqual(State.stopped, self.pomodoro.state)

        self.assertTrue(self.pomodoro.start())
        self.assertEqual(State.running, self.pomodoro.state)

        self.assertTrue(self.pomodoro.interrupt())
        self.assertEqual(State.stopped, self.pomodoro.state)

        self.assertEqual(None, self.pomodoro.interrupt())
        self.assertEqual(State.stopped, self.pomodoro.state)

        self.assertTrue(self.pomodoro.start())
        self.assertEqual(State.running, self.pomodoro.state)

        self.pomodoro._timer.running = True
        self.assertEqual(None, self.pomodoro.end())
        self.assertEqual(State.running, self.pomodoro.state)

        self.pomodoro._timer.running = False
        self.assertTrue(self.pomodoro.end())
        self.assertEqual(State.stopped, self.pomodoro.state)

    def test_should_reset_pomodoro_sessions(self):
        self.pomodoro.sessions = 10
        self.assertEqual(10, self.pomodoro.sessions)

        self.pomodoro.reset()
        self.assertEqual(0, self.pomodoro.sessions)

    @patch('tomate.profile.ProfileManager.get_int')
    def test_should_return_time_left_in_seconds(self, mget_int):
        from tomate.pomodoro import Pomodoro

        mget_int.return_value = 25
        pomodoro = Pomodoro()

        self.assertEqual(25 * 60, pomodoro.seconds_left)
        self.assertTrue(mget_int.called)
        mget_int.assert_called_once_with('Timer', 'pomodoro_duration')

    def test_should_not_change_task_when_pomodoro_is_running(self):
        self.pomodoro.state = State.running
        self.assertEqual(None, self.pomodoro.change_task())
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

    def test_should_change_task_when_pomodoro_is_stopped(self):
        self.pomodoro.state = State.stopped
        self.assertTrue(self.pomodoro.change_task(task=Task.shortbreak))
        self.assertEqual(Task.shortbreak, self.pomodoro.task)

    def test_should_increment_sessions_in_the_end_of_the_pomodoro_task(self):
        self.pomodoro.state = State.running

        self.assertTrue(self.pomodoro.end())
        self.assertEqual(1, self.pomodoro.sessions)
        self.assertEqual(Task.shortbreak, self.pomodoro.task)

        self.pomodoro.state = State.running

        self.assertTrue(self.pomodoro.end())
        self.assertEqual(1, self.pomodoro.sessions)
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

        self.pomodoro.state = State.running
        self.pomodoro.task = Task.longbreak

        self.assertTrue(self.pomodoro.end())
        self.assertEqual(1, self.pomodoro.sessions)
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

        self.pomodoro.state = State.running
        self.pomodoro.sessions = 3
        self.assertTrue(self.pomodoro.end())
        self.assertEqual(4, self.pomodoro.sessions)
        self.assertEqual(Task.longbreak, self.pomodoro.task)

    def test_should_return_pomodoro_status(self):
        self.pomodoro.sessions = 2
        self.pomodoro.task = Task.shortbreak
        self.pomodoro.state = State.running

        status = dict(task=Task.shortbreak,
                      sessions=2,
                      state=State.running,
                      time_left=5 * 60)

        self.assertEqual(status, self.pomodoro.status)


@patch('tomate.pomodoro.tomate_signals')
class PomodoroSignalTestCase(unittest.TestCase):

    def make_pomodoro(self):
        from tomate.pomodoro import Pomodoro

        return Pomodoro()

    @patch('tomate.profile.ProfileManager.get_int', return_value=25)
    def test_should_emit_session_started(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.start()

        mock_signals.emit.assert_called_once_with('session_started',
                                                  task=Task.pomodoro,
                                                  sessions=0,
                                                  state=State.running,
                                                  time_left=1500)

    @patch('tomate.profile.ProfileManager.get_int', return_value=25)
    def test_should_emit_session_interrupt(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.state = State.running
        pomodoro._timer.running = True
        pomodoro.interrupt()

        mock_signals.emit.assert_called_once_with('session_interrupted',
                                                  task=Task.pomodoro,
                                                  sessions=0,
                                                  state=State.stopped,
                                                  time_left=1500)

    @patch('tomate.profile.ProfileManager.get_int', return_value=25)
    def test_should_emit_session_reseted(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.sessions = 2
        pomodoro.reset()

        mock_signals.emit.assert_called_once_with('sessions_reseted',
                                                  task=Task.pomodoro,
                                                  sessions=0,
                                                  state=State.stopped,
                                                  time_left=1500)

    @patch('tomate.profile.ProfileManager.get_int', return_value=5)
    def test_should_emit_session_end(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.state = State.running
        pomodoro._timer.running = False
        pomodoro.end()

        mock_signals.emit.assert_called_once_with('session_ended',
                                                  task=Task.shortbreak,
                                                  sessions=1,
                                                  state=State.stopped,
                                                  time_left=300)

    @patch('tomate.profile.ProfileManager.get_int', return_value=15)
    def test_should_emit_task_changed(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.change_task(task=Task.longbreak)

        mock_signals.emit.assert_called_once_with('task_changed',
                                                  task=Task.longbreak,
                                                  sessions=0,
                                                  state=State.stopped,
                                                  time_left=900)
