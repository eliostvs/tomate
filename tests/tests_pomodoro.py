from __future__ import unicode_literals

import unittest

from mock import patch

from tomate.constants import State, Task


class PomodoroTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.pomodoro import Pomodoro

        self.pomodoro = Pomodoro()

    def test_default_state(self):
        self.assertEqual(Task.pomodoro, self.pomodoro.task)
        self.assertEqual(0, self.pomodoro.sessions)

    def test_session_start(self):
        self.pomodoro.state = State.running
        self.assertFalse(self.pomodoro.start())

        self.pomodoro.state = State.stopped
        self.assertTrue(self.pomodoro.start())
        self.assertEqual(State.running, self.pomodoro.state)

    def test_session_interrupt(self):
        self.pomodoro.state = State.stopped
        self.assertFalse(self.pomodoro.interrupt())

        self.pomodoro.state = State.running
        self.pomodoro._timer.running = True
        self.assertTrue(self.pomodoro.interrupt())
        self.assertEqual(State.stopped, self.pomodoro.state)

    def test_session_reset(self):
        self.pomodoro.state = State.running
        self.pomodoro.sessions = 10

        self.assertFalse(self.pomodoro.reset())

        self.pomodoro.state = State.stopped

        self.assertTrue(self.pomodoro.reset())
        self.assertEqual(0, self.pomodoro.sessions)

    def test_session_end(self):
        self.pomodoro.state = State.stopped
        self.pomodoro.sessions = 0
        self.assertFalse(self.pomodoro.end())

        self.pomodoro.state = State.running
        self.assertTrue(self.pomodoro.end())
        self.assertEqual(State.stopped, self.pomodoro.state)
        self.assertEqual(1, self.pomodoro.sessions)

    def test_session_status(self):
        self.pomodoro.sessions = 2
        self.pomodoro.task = Task.shortbreak
        self.pomodoro.state = State.running

        status = dict(task=Task.shortbreak,
                      sessions=2,
                      state=State.running,
                      time_left=5 * 60)

        self.assertEqual(status, self.pomodoro.status)

    @patch('tomate.profile.ProfileManager.get_int')
    def test_session_duration(self, mget_int):
        from tomate.pomodoro import Pomodoro

        mget_int.return_value = 25
        pomodoro = Pomodoro()

        self.assertEqual(25 * 60, pomodoro.session_duration)
        self.assertTrue(mget_int.called)
        mget_int.assert_called_once_with('Timer', 'pomodoro_duration')

    def test_change_task(self):
        self.pomodoro.state = State.running
        self.assertEqual(None, self.pomodoro.change_task())

        self.pomodoro.state = State.stopped
        self.assertTrue(self.pomodoro.change_task(task=Task.shortbreak))
        self.assertEqual(Task.shortbreak, self.pomodoro.task)


@patch('tomate.pomodoro.tomate_signals')
class TestPomodoroSignals(unittest.TestCase):

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
