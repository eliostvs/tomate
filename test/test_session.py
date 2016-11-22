from __future__ import unicode_literals

from mock import Mock
from tomate.constant import State, Task
from tomate.session import Session


def test_should_not_be_able_to_start_when_state_is_not_valid(session):
    session.state = State.started

    assert not session.start()


def test_should_be_able_to_start_when_state_is_valid(session):
    for state in (State.stopped, State.finished):
        session.state = state

        assert session.start()
        assert session.state


def test_shoud_not_be_able_to_stop_when_state_is_not_valid(session):
    session.state = State.stopped

    assert not session.stop()


def test_shoud_not_be_able_to_stop_when_state_is_valid_and_timer_is_not_running(session):
    session.timer.state = State.stopped
    session.state = State.stopped

    assert not session.stop()


def test_should_be_able_to_stop_when_state_is_valid(session):
    session.state = State.started
    session.timer.state = State.started

    assert session.stop()
    assert session.state == State.stopped


def test_should_no_be_able_to_reset_when_state_is_not_valid(session):
    session.state = State.started

    assert not session.reset()


def test_should_be_able_to_reset_whe_state_is_valid(session):
    for state in (State.stopped, State.finished):
        session.count = 10
        session.state = state

        assert session.reset()
        assert session.count == 0


def test_should_not_be_able_to_end_when_state_is_not_valid(session):
    session.state = State.stopped

    assert not session.end()


def test_should_not_be_able_to_end_when_the_state_is_valid_and_timer_is_running(session):
    session.state = State.started
    session.timer.state = State.started

    assert not session.end()


def test_should_be_able_to_end_when_state_is_valid_and_timer_is_not_running(session):
    session.state = State.started
    session.timer.state = State.stopped

    assert session.end()
    assert session.state == State.finished


def test_shoud_not_be_able_to_change_task_when_state_is_not_valid(session):
    session.state = State.started

    assert not session.change_task(task=None)


def test_should_be_able_to_change_task_when_state_is_valid(session):
    for state in (State.stopped, State.finished):
        session.timer.state = state

        session.change_task(dict(task=Task.shortbreak))

        assert session.change_task(task=Task.shortbreak)
        assert session.task == Task.shortbreak


def test_should_change_task_to_short_break(session):
    session.timer.state = State.stopped
    session.task = Task.pomodoro
    session.state = State.started
    session.count = 0
    session.config.get_int.return_value = 4

    session.end()

    assert session.task == Task.shortbreak


def test_should_change_task_to_pomodoro(session):
    for task in (Task.longbreak, Task.shortbreak):
        session.task = task
        session.timer.state = State.stopped
        session.state = State.started

        session.end()

        assert session.task == Task.pomodoro


def test_should_change_task_to_long_break(session):
    session.state = State.started
    session.task = Task.pomodoro
    session.count = 3
    session.config.get_int.return_value = 4

    assert session.end()
    assert session.task == Task.longbreak


def test_session_status(session):
    session.count = 2
    session.task = Task.shortbreak
    session.state = State.started
    session.config.get_int.return_value = 5

    expected = dict(task=Task.shortbreak,
                    sessions=2,
                    state=State.started,
                    time_left=5 * 60)

    assert session.status() == expected


def test_should_call_config(session):
    session.config.reset_mock()

    assert session.duration == 25 * 60
    session.config.get_int.assert_called_once_with('Timer', 'pomodoro_duration')


def test_should_trigger_start_event_when_session_start(session):
    session.start()

    session.event.send.assert_called_once_with(State.started,
                                               task=Task.pomodoro,
                                               sessions=0,
                                               state=State.started,
                                               time_left=1500)


def test_should_trigger_stop_event_when_session_stop(session):
    session.state = State.started
    session.timer.state = State.started
    session.stop()

    session.event.send.assert_called_with(State.stopped,
                                          task=Task.pomodoro,
                                          sessions=0,
                                          state=State.stopped,
                                          time_left=1500)


def test_should_trigger_changed_event_when_session_reset(session):
    session.count = 2
    session.reset()

    session.event.send.assert_called_with(State.reset,
                                          task=Task.pomodoro,
                                          sessions=0,
                                          state=State.stopped,
                                          time_left=1500)


def test_should_trigger_finished_event(session):
    session.state = State.started
    session.timer.State = State.stopped
    session.config.get_int.return_value = 5
    session.end()

    session.event.send.assert_called_with(State.finished,
                                          task=Task.shortbreak,
                                          sessions=1,
                                          state=State.finished,
                                          time_left=300)


def test_should_trigger_changed_event_when_task_change(session):
    session.config.get_int.return_value = 15
    session.change_task(task=Task.longbreak)

    session.event.send.assert_called_with(State.changed,
                                          task=Task.longbreak,
                                          sessions=0,
                                          state=State.stopped,
                                          time_left=900)


def test_module(graph, config):
    assert 'tomate.session' in graph.providers

    graph.register_instance('tomate.timer', Mock())
    graph.register_instance('tomate.config', config)
    graph.register_instance('tomate.events.session', Mock())

    assert isinstance(graph.get('tomate.session'), Session)
