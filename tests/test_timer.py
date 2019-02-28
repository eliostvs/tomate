import pytest
from wiring import SingletonScope
from wiring.scanning import scan_to_graph

from tomate.constant import State
from tomate.timer import Timer, TimerPayload


@pytest.fixture()
def subject(mocker):
    from tomate.timer import Timer

    return Timer(dispatcher=mocker.Mock())


class TestEventPayload:
    def test_should_be_zero_when_duration_is_zero(self):
        # Given
        payload = TimerPayload(duration=0, time_left=1)

        # Then
        assert payload.ratio == 0.0

    def test_should_be_zero_percent_when_timer_ends(self):
        payload = TimerPayload(duration=1, time_left=1)

        assert payload.ratio == 0.0

    def test_should_be_one_hundred_percent_when_the_timer_starts(self):
        payload = TimerPayload(duration=1, time_left=0)

        assert payload.ratio == 1.0

    def test_should_be_fifty_percent_when_half_of_time_has_passed(self):
        payload = TimerPayload(duration=10, time_left=5)

        assert payload.ratio == 0.5


class TestTimerStop:
    def test_should_not_be_able_to_stop_when_timer_is_not_running(self, subject):
        subject.state = State.stopped

        assert not subject.stop()

    def test_should_be_able_to_stop_when_timer_is_running(self, subject):
        subject.state = State.started

        assert subject.stop()
        assert subject.state == State.stopped


class TestTimerStart:
    def test_should_not_be_able_to_start_when_timer_is_already_running(self, subject):
        subject.state = State.started

        assert not subject.start(1)

    def test_should_be_able_to_start_when_timer_is_stopped(self, subject):
        subject.state = State.stopped

        assert subject.start(1)

    def test_should_be_able_to_start_when_timer_is_finished(self, subject):
        subject.state = State.finished

        assert subject.start(1)

    def test_should_update_time_left_and_duration_when_timer_start(self, subject):
        subject.state = State.finished

        subject.start(5)

        assert subject.time_left == 5
        assert subject.duration == 5

    def test_should_trigger_started_event_when_timer_start(self, subject):
        subject.start(10)

        subject._dispatcher.send.assert_called_with(
            State.started, payload=TimerPayload(time_left=10, duration=10)
        )


class TestTimerUpdate:
    def test_should_not_update_when_timer_is_not_started(self, subject):
        # Given
        subject.state = State.stopped

        # Then
        assert subject._update() is False

    def test_should_decrease_the_time_left_after_update(self, subject):
        subject.start(2)

        assert subject._update()
        assert subject.time_left == 1

    def test_should_keep_duration_after_update(self, subject):
        duration = 10

        subject.start(duration)

        assert subject._update()

        assert subject.duration == duration

    def test_should_trigger_changed_event_after_update(self, subject):
        subject.start(10)

        subject._update()

        subject._dispatcher.send.assert_called_with(
            State.changed, payload=TimerPayload(time_left=9, duration=10)
        )


class TestTimerEnd:
    def test_should_trigger_finished_event_when_time_ends(self, subject):
        subject.start(1)

        subject._update()
        subject._update()

        subject._dispatcher.send.assert_called_with(
            State.finished, payload=TimerPayload(time_left=0, duration=1)
        )


def test_module(graph, mocker):
    spec = "tomate.timer"

    scan_to_graph([spec], graph)

    assert spec in graph.providers

    provider = graph.providers[spec]

    assert provider.scope == SingletonScope

    graph.register_factory("tomate.events.timer", mocker.Mock)

    assert isinstance(graph.get(spec), Timer)
