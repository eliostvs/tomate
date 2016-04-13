from __future__ import unicode_literals

import pytest
from mock import Mock

from tomate.constant import State
from tomate.event import Events


@pytest.fixture()
def timer():
    from tomate.timer import Timer

    return Timer(events=Events)


@pytest.fixture()
def session(timer):
    from tomate.session import Session

    Events.Setting.receivers.clear()

    return Session(timer=timer,
                    config=Mock(**{'get_int.return_value': 0.01}),
                    events=Events)


def test_should_change_state_to_finished(timer, session):
    session.start()

    timer._update()
    timer._update()

    assert State.finished == session.state


def test_call_to_change_task_should_be_true_when_session_is_stopped(session):
    result = Events.Setting.send('timer')

    assert [(session.change_task, True)] == result


def test_call_to_change_task_should_be_false_when_session_is_started(session):
    session.state = State.started

    result = Events.Setting.send('timer')

    assert [(session.change_task, False)] == result
