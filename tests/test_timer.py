from unittest.mock import Mock

from wiring import SingletonScope

from tomate.constant import State
from tomate.timer import Timer, EventPayload


class TestEventPayload:
    def test_should_be_zero_percent_when_timer_ends(self):
        payload = EventPayload(duration=1, time_left=1)

        assert payload.ratio == 0.0

    def test_should_be_one_hundred_percent_when_the_timer_starts(self):
        payload = EventPayload(duration=1, time_left=0)

        assert payload.ratio == 1.0

    def test_should_be_fifty_percent_when_half_of_time_has_passed(self):
        payload = EventPayload(duration=10, time_left=5)

        assert payload.ratio == 0.5


class TestTimerStop:
    def test_should_not_be_able_to_stop_when_timer_is_not_running(self, timer):
        timer.state = State.stopped

        assert not timer.stop()

    def test_should_be_able_to_stop_when_timer_is_running(self, timer):
        timer.state = State.started

        assert timer.stop()
        assert timer.state == State.stopped


class TestTimerStart:
    def test_should_not_be_able_to_start_when_timer_is_already_running(self, timer):
        timer.state = State.started

        assert not timer.start(1)

    def test_should_be_able_to_start_when_timer_is_stopped(self, timer):
        timer.state = State.stopped

        assert timer.start(1)

    def test_should_be_able_to_start_when_timer_is_finished(self, timer):
        timer.state = State.finished

        assert timer.start(1)

    def test_should_update_time_left_and_duration_when_timer_start(self, timer):
        timer.state = State.finished

        timer.start(5)

        assert timer.time_left == 5
        assert timer.duration == 5

    def test_should_trigger_started_event_when_timer_start(self, timer):
        timer.start(10)

        timer._dispatcher.send.assert_called_with(
            State.started, payload=EventPayload(time_left=10, duration=10)
        )


class TestTimerUpdate:
    def test_should_decrease_the_time_left_after_update(self, timer):
        timer.start(2)

        assert timer._update()
        assert timer.time_left == 1

    def test_should_keep_duration_after_update(self, timer):
        duration = 10

        timer.start(duration)

        assert timer._update()

        assert timer.duration == duration

    def test_should_trigger_changed_event_after_update(self, timer):
        timer.start(10)

        timer._update()

        timer._dispatcher.send.assert_called_with(
            State.changed, payload=EventPayload(time_left=9, duration=10)
        )


class TestTimerEnd:
    def test_should_trigger_finished_event_when_time_ends(self, timer):
        timer.start(1)

        timer._update()
        timer._update()

        timer._dispatcher.send.assert_called_with(
            State.finished, payload=EventPayload(time_left=0, duration=1)
        )


def test_module(graph):
    assert "tomate.timer" in graph.providers

    provider = graph.providers["tomate.timer"]

    assert provider.scope == SingletonScope

    graph.register_instance("tomate.events.timer", Mock())

    assert isinstance(graph.get("tomate.timer"), Timer)
