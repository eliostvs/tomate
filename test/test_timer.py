from __future__ import division, unicode_literals

import pytest
from mock import Mock
from wiring import FactoryProvider, SingletonScope

from tomate.constant import State
from tomate.graph import graph
from tomate.timer import Timer, TimerModule


@pytest.fixture()
def timer():
    return Timer(events=Mock())


def test_default_timer_values(timer):
    assert timer.state == State.stopped
    assert timer.time_ratio == 0
    assert timer.time_left == 0


def test_should_not_be_able_to_stop_when_timer_is_not_running(timer):
    timer.state = State.stopped

    assert not timer.stop()


def test_should_be_able_to_stop_when_timer_is_running(timer):
    timer.state = State.started

    assert timer.stop()
    assert timer.state == State.stopped


def test_should_not_be_able_to_start_when_timer_is_alread_running(timer):
    timer.state = State.started

    assert not timer.start(1)


def test_should_be_able_to_start_when_timer_is_not_running(timer):
    timer.state = State.stopped

    assert timer.start(1)


def test_should_be_able_to_start_when_timer_is_finished(timer):
    timer.state = State.finished

    assert timer.start(1)


def test_should_update_seconds_when_timer_start(timer):
    timer.state = State.finished

    timer.start(1)

    assert timer.time_left == 1
    assert timer._Timer__seconds == 1


def test_should_increase_the_time_ratio_after_update(timer):
    assert timer.time_ratio == 0

    timer.start(10)

    timer._update()
    timer._update()
    timer._update()

    assert timer.time_ratio == 0.3


def test_should_decrease_the_time_left_after_update(timer):
    assert not timer._update()

    timer.start(2)

    assert timer._update()
    assert timer.time_left == 1


def test_should_finished_when_the_time_ends(timer):
    timer.start(1)

    timer._update()
    timer._update()

    assert timer.state == State.finished


def test_should_trigger_finished_event(timer):
    timer.start(1)

    timer._update()
    timer._update()

    timer.event.send.assert_called_with(State.finished, time_left=0, time_ratio=0)


def test_should_trigger_changed_event(timer):
    timer.start(10)

    timer._update()

    timer.event.send.assert_called_with(State.changed, time_left=9, time_ratio=0.1)


def test_module():
    assert ['tomate.timer'] == list(TimerModule.providers.keys())

    TimerModule().add_to(graph)

    provider = graph.providers['tomate.timer']

    assert isinstance(provider, FactoryProvider)
    assert provider.scope == SingletonScope

    assert {'events': 'tomate.events'} == provider.dependencies

    graph.register_instance('tomate.events', Mock())
    assert isinstance(graph.get('tomate.timer'), Timer)
