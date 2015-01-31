from __future__ import unicode_literals

import unittest

from mock import patch
from tomate.pomodoro import Task


class PomodoroTaskTestCase(unittest.TestCase):

    def test_get_task_by_index(self):
        self.assertEqual(Task.pomodoro, Task.get_by_index(0))


class PomodoroTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.pomodoro import Pomodoro

        self.pomodoro = Pomodoro()

    def test_pomodoro_init_values(self):
        self.assertEqual(Task.pomodoro, self.pomodoro.task)
        self.assertEqual(0, self.pomodoro.sessions)

    def test_change_pomodoro_states(self):
        self.assertEqual('stopped', self.pomodoro.state)

        self.assertTrue(self.pomodoro.start())
        self.assertEqual('running', self.pomodoro.state)

        self.assertTrue(self.pomodoro.interrupt())
        self.assertEqual('stopped', self.pomodoro.state)

        self.assertEqual(None, self.pomodoro.interrupt())
        self.assertEqual('stopped', self.pomodoro.state)

        self.assertTrue(self.pomodoro.start())
        self.assertEqual('running', self.pomodoro.state)

        self.pomodoro._timer.running = True
        self.assertEqual(None, self.pomodoro.end())
        self.assertEqual('running', self.pomodoro.state)

        self.pomodoro._timer.running = False
        self.assertTrue(self.pomodoro.end())
        self.assertEqual('stopped', self.pomodoro.state)

    def test_reset_sessions(self):
        self.pomodoro.sessions = 10

        self.pomodoro.reset()

        self.assertEqual(0, self.pomodoro.sessions)

    @patch('tomate.profile.ProfileManager.get_int')
    def test_session_duration(self, mget_int):
        from tomate.pomodoro import Pomodoro

        mget_int.return_value = 25
        pomodoro = Pomodoro()

        self.assertEqual(25 * 60, pomodoro.seconds_left)
        self.assertTrue(mget_int.called)
        mget_int.assert_called_once_with('Timer', 'pomodoro_duration')

        mget_int.reset_mock()
        mget_int.return_value = 5
        pomodoro.task = Task.shortbreak

        self.assertEqual(5 * 60, pomodoro.seconds_left)
        self.assertTrue(mget_int.called)
        mget_int.assert_called_once_with('Timer', 'shortbreak_duration')

    def test_change_pomodoro_task(self):
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

        self.pomodoro.state = 'running'
        self.assertEqual(None, self.pomodoro.change_task())
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

        self.pomodoro.state = 'stopped'
        self.assertTrue(self.pomodoro.change_task(task=Task.shortbreak))
        self.assertEqual(Task.shortbreak, self.pomodoro.task)

    def test_pomodoro_session_end(self):
        self.pomodoro.state = 'running'

        self.assertTrue(self.pomodoro.end())
        self.assertEqual(1, self.pomodoro.sessions)
        self.assertEqual(Task.shortbreak, self.pomodoro.task)

        self.pomodoro.state = 'running'

        self.assertTrue(self.pomodoro.end())
        self.assertEqual(1, self.pomodoro.sessions)
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

        self.pomodoro.state = 'running'
        self.pomodoro.task = Task.longbreak

        self.assertTrue(self.pomodoro.end())
        self.assertEqual(1, self.pomodoro.sessions)
        self.assertEqual(Task.pomodoro, self.pomodoro.task)

        self.pomodoro.state = 'running'
        self.pomodoro.sessions = 3
        self.assertTrue(self.pomodoro.end())
        self.assertEqual(4, self.pomodoro.sessions)
        self.assertEqual(Task.longbreak, self.pomodoro.task)


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
                                                  time_left=1500)

    @patch('tomate.profile.ProfileManager.get_int', return_value=25)
    def test_should_emit_session_interrupt(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.state = 'running'
        pomodoro._timer.running = True
        pomodoro.interrupt()

        mock_signals.emit.assert_called_once_with('session_interrupted',
                                                  task=Task.pomodoro,
                                                  sessions=0,
                                                  time_left=1500)

    @patch('tomate.profile.ProfileManager.get_int', return_value=25)
    def test_should_emit_session_reseted(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.sessions = 2
        pomodoro.reset()

        mock_signals.emit.assert_called_once_with('sessions_reseted',
                                                  task=Task.pomodoro,
                                                  sessions=0,
                                                  time_left=1500)

    @patch('tomate.profile.ProfileManager.get_int', return_value=5)
    def test_should_emit_session_end(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.state = 'running'
        pomodoro._timer.running = False
        pomodoro.end()

        mock_signals.emit.assert_called_once_with('session_ended',
                                                  task=Task.shortbreak,
                                                  sessions=1,
                                                  time_left=300)

    @patch('tomate.profile.ProfileManager.get_int', return_value=15)
    def test_should_emit_task_changed(self, mget_int, mock_signals):
        pomodoro = self.make_pomodoro()
        pomodoro.change_task(task=Task.longbreak)

        mock_signals.emit.assert_called_once_with('task_changed',
                                                  task=Task.longbreak,
                                                  sessions=0,
                                                  time_left=900)
