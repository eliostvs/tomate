from unittest.mock import Mock

from wiring import SingletonScope

from tomate.constant import State
from tomate.timer import Timer


def test_timer_initial_values(timer):
    assert timer.state == State.stopped
    assert timer.time_ratio == 0
    assert timer.seconds_left == 0


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

    def test_should_update_seconds_left_and_total_seconds_when_timer_start(self, timer):
        timer.state = State.finished

        timer.start(5)

        assert timer.seconds_left == 5
        assert timer.total_seconds == 5

    def test_should_trigger_started_event_when_timer_start(self, timer):
        timer.start(10)

        timer._dispatcher.send.assert_called_with(State.started, time_left=10, time_ratio=0.0, time_total=10)


class TestTimerUpdate:
    def test_should_increase_the_time_ratio_after_update(self, timer):
        timer.start(10)

        timer._update()
        timer._update()
        timer._update()

        assert timer.time_ratio == 0.3

    def test_should_decrease_the_time_left_after_update(self, timer):
        timer.start(2)

        assert timer._update()
        assert timer.seconds_left == 1

    def test_should_keep_total_seconds_after_update(self, timer):
        total_seconds = 10

        timer.start(total_seconds)

        assert timer._update()

        assert timer.total_seconds == total_seconds

    def test_should_trigger_changed_event_after_update(self, timer):
        timer.start(10)

        timer._update()

        timer._dispatcher.send.assert_called_with(State.changed, time_left=9, time_ratio=0.1, time_total=10)


class TestTimerEnd:
    def test_should_trigger_finished_event_when_time_ends(self, timer):
        timer.start(1)

        timer._update()
        timer._update()

        timer._dispatcher.send.assert_called_with(State.finished, time_left=0, time_ratio=1, time_total=1)


def test_module(graph):
    assert 'tomate.timer' in graph.providers

    provider = graph.providers['tomate.timer']

    assert provider.scope == SingletonScope

    graph.register_instance('tomate.events.timer', Mock())

    assert isinstance(graph.get('tomate.timer'), Timer)
