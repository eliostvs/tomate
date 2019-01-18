import pytest
from tomate.constant import State, Sessions
from tomate.session import Session, SECONDS_IN_A_MINUTE, SessionPayload, FinishedSession
from wiring import SingletonScope


@pytest.fixture
def timer_payload(mocker):
    return mocker.Mock(duration=0)


class TestCountPomodoro:
    def test_count_of_pomodoro(self):
        payload = SessionPayload(
            duration=0,
            state=None,
            task="",
            type=None,
            sessions=[
                FinishedSession(0, Sessions.pomodoro, 0),
                FinishedSession(0, Sessions.pomodoro, 0),
                FinishedSession(0, Sessions.shortbreak, 0),
                FinishedSession(0, Sessions.longbreak, 0),
            ],
        )
        assert len(payload.finished_pomodoros) == 2


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

        payload = SessionPayload(
            duration=25 * SECONDS_IN_A_MINUTE,
            sessions=[],
            state=State.started,
            task="",
            type=Sessions.pomodoro,
        )

        session._dispatcher.send.assert_called_once_with(State.started, payload=payload)


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

        payload = SessionPayload(
            duration=25 * SECONDS_IN_A_MINUTE,
            sessions=[],
            state=State.stopped,
            task="",
            type=Sessions.pomodoro,
        )

        session._dispatcher.send.assert_called_with(State.stopped, payload=payload)


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

        payload = SessionPayload(
            duration=25 * SECONDS_IN_A_MINUTE,
            sessions=[],
            state=State.finished,
            task="",
            type=Sessions.pomodoro,
        )

        session._dispatcher.send.assert_called_with(State.reset, payload=payload)


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
        self, session, timer_payload
    ):
        session.state = State.started
        session._timer.state = State.stopped

        assert session.end(None, payload=timer_payload)
        assert session.state == State.finished

    def test_should_automatically_change_session_to_short_break(
        self, session, timer_payload
    ):
        session._timer.state = State.stopped
        session.current = Sessions.pomodoro
        session.state = State.started
        session.count = 0
        session._config.get_int.return_value = 4

        session.end(None, timer_payload)

        assert session.current == Sessions.shortbreak

    def test_should_automatically_change_session_to_long_break(
        self, session, timer_payload
    ):
        session.state = State.started
        session.current = Sessions.pomodoro
        session.sessions = [
            FinishedSession(id=0, type=Sessions.pomodoro, duration=0)
        ] * 3
        session._config.get_int.return_value = 4

        assert session.end(None, payload=timer_payload)
        assert session.current == Sessions.longbreak

    def test_should_automatically_change_session_to_pomodoro(
        self, session, timer_payload
    ):
        for session_type in (Sessions.longbreak, Sessions.shortbreak):
            session.current = session_type
            session._timer.state = State.stopped
            session.state = State.started

            session.end(None, timer_payload)

            assert session.current == Sessions.pomodoro

    def test_should_trigger_finished_event(self, session, mocker):
        duration = 25 * SECONDS_IN_A_MINUTE
        session.state = State.started
        session._timer.State = State.stopped

        session.current = Sessions.pomodoro

        session.end(None, payload=mocker.Mock(duration=duration))

        payload = SessionPayload(
            type=Sessions.shortbreak,
            sessions=[
                FinishedSession(
                    id=mocker.ANY, type=Sessions.pomodoro, duration=duration
                )
            ],
            state=State.finished,
            duration=25 * SECONDS_IN_A_MINUTE,
            task="",
        )

        session._dispatcher.send.assert_called_with(State.finished, payload=payload)


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

        payload = SessionPayload(
            type=Sessions.longbreak,
            sessions=[],
            state=State.stopped,
            duration=15 * SECONDS_IN_A_MINUTE,
            task="",
        )

        session._dispatcher.send.assert_called_with(State.changed, payload=payload)


class TestChangeTask:
    def test_initial_task(self, session):
        assert session.task == ""

    def test_change_task_when_session_is_stopped_should_work(self, session):
        session.state = State.stopped
        session.task = "new task name"

        assert session.task == "new task name"

    def test_change_task_when_session_is_finished_should_work(self, session):
        session.state = State.finished
        session.task = "new task name"

        assert session.task == "new task name"

    def test_change_task_when_session_is_running_should_not_work(self, session):
        session.state = State.started

        session.task = "new task name"

        assert session.task == ""


def test_module(graph, config, mocker):
    assert "tomate.session" in graph.providers

    provider = graph.providers["tomate.session"]
    assert provider.scope == SingletonScope

    graph.register_instance("tomate.timer", mocker.Mock())
    graph.register_instance("tomate.config", config)
    graph.register_instance("tomate.events.session", mocker.Mock())

    assert isinstance(graph.get("tomate.session"), Session)
