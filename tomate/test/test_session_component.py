from __future__ import unicode_literals

import unittest

from mock import Mock

from tomate.enums import State
from tomate.events import Events
from tomate.session import Session
from tomate.timer import Timer


class SessionComponent(unittest.TestCase):

    def test_should_session_state_be_finished(self):
        timer = Timer(events=Events)
        session = Session(timer=timer,
                               config=Mock(**{'get_int.return_value': 0.01}),
                               events=Events)
        session.start()

        timer.update()
        timer.update()

        self.assertEqual(State.finished, session.state)
