from __future__ import unicode_literals

import unittest

from mock import Mock

from tomate.enums import State
from tomate.events import Events
from tomate.session import Session
from tomate.timer import Timer
from blinker import ANY


class SessionComponent(unittest.TestCase):

    def setUp(self):
        Events.Setting.receivers.clear()

        self.timer = Timer(events=Events)
        self.session = Session(timer=self.timer,
                               config=Mock(**{'get_int.return_value': 0.01}),
                               events=Events)

    def test_should_change_state_to_finished(self):
        self.session.start()

        self.timer.update()
        self.timer.update()

        self.assertEqual(State.finished, self.session.state)

    def test_call_change_task_when_setting_event_emit_and_session_stopped_should_success(self):
        result = Events.Setting.send('timer')

        self.assertEqual([(self.session.change_task, True)], result)

    def test_call_change_task_when_setting_event_emit_and_session_running_should_fail(self):
        self.session.state = State.running

        result = Events.Setting.send('timer')

        self.assertEqual([(self.session.change_task, False)], result)
