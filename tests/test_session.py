from unittest.mock import Mock

from wiring import SingletonScope

from tomate.constant import State, Sessions
from tomate.session import Session, SECONDS_IN_A_MINUTE


def test_should_not_be_able_to_start_when_state_is_not_valid(session):
    session.state = State.started

    assert not session.start()


def test_should_be_able_to_start_when_state_is_valid(session):
    for state in (State.stopped, State.finished):
        session.state = state

        assert session.start()
        assert session.state


def test_should_not_be_able_to_stop_when_state_is_not_valid(session):
    session.state = State.stopped

    assert not session.stop()


def test_should_not_be_able_to_stop_when_state_is_valid_and_timer_is_not_running(session):
    session._timer.state = State.stopped
    session.state = State.stopped

    assert not session.stop()


def test_should_be_able_to_stop_when_state_is_valid(session):
    session.state = State.started
    session._timer.state = State.started

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
    session._timer.state = State.started

    assert not session.end()


def test_should_be_able_to_end_when_state_is_valid_and_timer_is_not_running(session):
    session.state = State.started
    session._timer.state = State.stopped

    assert session.end()
    assert session.state == State.finished


def test_should_not_be_able_to_change_task_when_state_is_not_valid(session):
    session.state = State.started

    assert not session.change_task(task=None)


def test_should_be_able_to_change_task_when_state_is_valid(session):
    for state in (State.stopped, State.finished):
        session._timer.state = state

        session.change_task(dict(task=Sessions.shortbreak))

        assert session.change_task(task=Sessions.shortbreak)
        assert session.task == Sessions.shortbreak


def test_should_change_task_to_short_break(session):
    session._timer.state = State.stopped
    session.task = Sessions.pomodoro
    session.state = State.started
    session.count = 0
    session._config.get_int.return_value = 4

    session.end()

    assert session.task == Sessions.shortbreak


def test_should_change_task_to_pomodoro(session):
    for task in (Sessions.longbreak, Sessions.shortbreak):
        session.task = task
        session._timer.state = State.stopped
        session.state = State.started

        session.end()

        assert session.task == Sessions.pomodoro


def test_should_change_task_to_long_break(session):
    session.state = State.started
    session.task = Sessions.pomodoro
    session.count = 3
    session._config.get_int.return_value = 4

    assert session.end()
    assert session.task == Sessions.longbreak


def test_session_status(session):
    session.count = 2
    session.task = Sessions.shortbreak
    session.state = State.started
    session._config.get_int.return_value = 5

    expected = dict(task=Sessions.shortbreak,
                    sessions=2,
                    state=State.started,
                    time_left=5 * SECONDS_IN_A_MINUTE,
                    task_name='')

    assert session.status() == expected


def test_should_call_config(session):
    session._config.reset_mock()

    assert session.duration == 25 * SECONDS_IN_A_MINUTE
    session._config.get_int.assert_called_once_with('Timer', 'pomodoro_duration')


def test_should_trigger_start_event_when_session_start(session):
    session.start()

    session._dispatcher.send.assert_called_once_with(State.started,
                                                     task=Sessions.pomodoro,
                                                     sessions=0,
                                                     state=State.started,
                                                     time_left=1500,
                                                     task_name='')


def test_should_trigger_stop_event_when_session_stop(session):
    session.state = State.started
    session._timer.state = State.started
    session.stop()

    session._dispatcher.send.assert_called_with(State.stopped,
                                                task=Sessions.pomodoro,
                                                sessions=0,
                                                state=State.stopped,
                                                time_left=1500,
                                                task_name='')


def test_should_trigger_changed_event_when_session_reset(session):
    session.count = 2
    session.reset()

    session._dispatcher.send.assert_called_with(State.reset,
                                                task=Sessions.pomodoro,
                                                sessions=0,
                                                state=State.stopped,
                                                time_left=1500,
                                                task_name='')


def test_should_trigger_finished_event(session):
    session.state = State.started
    session._timer.State = State.stopped
    session._config.get_int.return_value = 5
    session.end()

    session._dispatcher.send.assert_called_with(State.finished,
                                                task=Sessions.shortbreak,
                                                sessions=1,
                                                state=State.finished,
                                                time_left=300,
                                                task_name='')


def test_should_trigger_changed_event_when_task_change(session):
    session._config.get_int.return_value = 15
    session.change_task(task=Sessions.longbreak)

    session._dispatcher.send.assert_called_with(State.changed,
                                                task=Sessions.longbreak,
                                                sessions=0,
                                                state=State.stopped,
                                                time_left=900,
                                                task_name='')


def test_initial_task_name(session):
    assert session.task_name == ''


def test_change_task_name_when_session_is_stopped_should_work(session):
    session.state = State.stopped
    session.task_name = 'new task name'

    assert session.task_name == 'new task name'


def test_change_task_name_when_session_is_finished_should_work(session):
    session.state = State.finished
    session.task_name = 'new task name'

    assert session.task_name == 'new task name'


def test_change_task_name_when_session_is_running_should_not_work(session):
    session.state = State.started

    session.task_name = 'new task name'

    assert session.task_name == ''


def test_module(graph, config):
    assert 'tomate.session' in graph.providers

    provider = graph.providers['tomate.session']
    assert provider.scope == SingletonScope

    graph.register_instance('tomate.timer', Mock())
    graph.register_instance('tomate.config', config)
    graph.register_instance('tomate.events.session', Mock())

    assert isinstance(graph.get('tomate.session'), Session)
