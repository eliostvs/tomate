import uuid

from wiring import SingletonScope

from tomate.constant import State, Sessions
from tomate.session import Session, SECONDS_IN_A_MINUTE


class TestCountPomodoro:
    def test_count_of_pomodoro(self):
        sessions = [
            (0, Sessions.pomodoro, 0),
            (0, Sessions.pomodoro, 0),
            (0, Sessions.shortbreak, 0),
            (0, Sessions.longbreak, 0),
        ]

        assert Session.count_pomodoros(sessions) == 2


class TestSessionStart:
    def test_should_not_be_able_to_start_when_session_already_started(self, session):
        session.state = State.started

        assert not session.start()

    def test_should_be_able_to_start_when_session_is_finished(self, session):
        session.state = State.finished

        assert session.start()
        assert session.state

    def test_should_be_able_to_start_when_session_is_stopped(self, session):
        session.state = State.stopped

        assert session.start()
        assert session.state

    def test_should_trigger_start_event_when_session_start(self, session):
        session.start()

        session._dispatcher.send.assert_called_once_with(
            State.started,
            current=Sessions.pomodoro,
            sessions=[],
            state=State.started,
            duration=25 * SECONDS_IN_A_MINUTE,
            task_name="",
        )


class TestSessionStop:
    def test_should_not_be_able_to_stop_when_session_is_not_started_but_time_it_is(
            self, session
    ):
        session._timer.state = State.started
        session.state = State.stopped

        assert not session.stop()

    def test_should_not_be_able_to_stop_when_session_started_but_timer_is_not(
            self, session
    ):
        session._timer.state = State.stopped
        session.state = State.started

        assert not session.stop()

    def test_should_be_able_to_stop_when_session_and_timer_is_running(self, session):
        session._timer.state = State.started
        session.state = State.started

        assert session.stop()

        assert session.state == State.stopped

    def test_should_trigger_stop_event_when_session_stop(self, session):
        session.state = State.started
        session._timer.state = State.started
        session.stop()

        session._dispatcher.send.assert_called_with(
            State.stopped,
            current=Sessions.pomodoro,
            sessions=[],
            state=State.stopped,
            duration=25 * SECONDS_IN_A_MINUTE,
            task_name="",
        )


class TestSessionReset:
    def test_should_not_be_able_to_reset_when_session_is_started(self, session):
        session.state = State.started

        assert not session.reset()

    def test_should_be_able_to_reset_when_session_is_stopped(self, session):
        session.state = State.stopped
        session.sessions = [(Sessions.pomodoro, 25 * SECONDS_IN_A_MINUTE)]

        assert session.reset()
        assert session.sessions == []

    def test_should_be_able_to_reset_whe_session_is_finished(self, session):
        session.state = State.finished
        session.sessions = [(Sessions.pomodoro, 25 * SECONDS_IN_A_MINUTE)]

        assert session.reset()
        assert session.sessions == []

    def test_should_trigger_changed_event_when_session_reset(self, session):
        session.state = State.finished
        session.sessions = [(Sessions.pomodoro, 25 * SECONDS_IN_A_MINUTE)]

        session.reset()

        session._dispatcher.send.assert_called_with(
            State.reset,
            current=Sessions.pomodoro,
            sessions=[],
            state=State.finished,
            duration=25 * SECONDS_IN_A_MINUTE,
            task_name="",
        )


class TestEndSession:
    def test_should_not_be_able_to_end_when_state_is_not_valid(self, session):
        session.state = State.stopped

        assert not session.end()

    def test_should_not_be_able_to_end_when_the_state_is_valid_and_timer_is_running(
            self, session
    ):
        session.state = State.started
        session._timer.state = State.started

        assert not session.end()

    def test_should_be_able_to_end_when_state_is_valid_and_timer_is_not_running(
            self, session
    ):
        session.state = State.started
        session._timer.state = State.stopped

        assert session.end()
        assert session.state == State.finished

    def test_should_automatically_change_session_to_short_break(self, session):
        session._timer.state = State.stopped
        session.current = Sessions.pomodoro
        session.state = State.started
        session.count = 0
        session._config.get_int.return_value = 4

        session.end()

        assert session.current == Sessions.shortbreak

    def test_should_automatically_change_session_to_long_break(self, session):
        session.state = State.started
        session.current = Sessions.pomodoro
        session.sessions = [(uuid.uuid4(), Sessions.pomodoro, 0)] * 3
        session._config.get_int.return_value = 4

        assert session.end()
        assert session.current == Sessions.longbreak

    def test_should_automatically_change_session_to_pomodoro(self, session):
        for session_type in (Sessions.longbreak, Sessions.shortbreak):
            session.current = session_type
            session._timer.state = State.stopped
            session.state = State.started

            session.end()

            assert session.current == Sessions.pomodoro

    def test_should_trigger_finished_event(self, session, mocker):
        time_total = 25 * SECONDS_IN_A_MINUTE
        session.state = State.started
        session._timer.State = State.stopped

        session.current = Sessions.pomodoro

        session.end(time_total=time_total)

        session._dispatcher.send.assert_called_with(
            State.finished,
            current=Sessions.shortbreak,
            sessions=[(mocker.ANY, Sessions.pomodoro, time_total)],
            state=State.finished,
            duration=25 * SECONDS_IN_A_MINUTE,
            task_name="",
        )


class TestChangeSessionType:
    def test_should_not_be_able_to_change_session_type_when_session_already_started(
            self, session
    ):
        session.state = State.started

        assert not session.change(session=None)

    def test_should_be_able_to_change_session_type_when_session_is_not_started(
            self, session
    ):
        for state in (State.stopped, State.finished):
            session._timer.state = state

            assert session.change(session=Sessions.shortbreak)
            assert session.current == Sessions.shortbreak

    def test_should_trigger_changed_event_when_session_type_change(self, session):
        session._config.get_int.return_value = 15
        session.change(session=Sessions.longbreak)

        session._dispatcher.send.assert_called_with(
            State.changed,
            current=Sessions.longbreak,
            sessions=[],
            state=State.stopped,
            duration=15 * SECONDS_IN_A_MINUTE,
            task_name="",
        )


class TestSessionStatus:
    def test_session_status(self, session):
        session.current = Sessions.shortbreak
        session.state = State.started
        session._config.get_int.return_value = 5

        expected = dict(
            current=Sessions.shortbreak,
            sessions=[],
            state=State.started,
            duration=5 * SECONDS_IN_A_MINUTE,
            task_name="",
        )

        assert session.status == expected


class TestChangeTaskName:
    def test_initial_task_name(self, session):
        assert session.task_name == ""

    def test_change_task_name_when_session_is_stopped_should_work(self, session):
        session.state = State.stopped
        session.task_name = "new task name"

        assert session.task_name == "new task name"

    def test_change_task_name_when_session_is_finished_should_work(self, session):
        session.state = State.finished
        session.task_name = "new task name"

        assert session.task_name == "new task name"

    def test_change_task_name_when_session_is_running_should_not_work(self, session):
        session.state = State.started

        session.task_name = "new task name"

        assert session.task_name == ""


def test_module(graph, config, mocker):
    assert "tomate.session" in graph.providers

    provider = graph.providers["tomate.session"]
    assert provider.scope == SingletonScope

    graph.register_instance("tomate.timer", mocker.Mock())
    graph.register_instance("tomate.config", config)
    graph.register_instance("tomate.events.session", mocker.Mock())

    assert isinstance(graph.get("tomate.session"), Session)
