from collections import namedtuple

from gi.repository import GLib
from wiring import inject, SingletonScope
from wiring.scanning import register

from .constant import State
from .event import ObservableProperty
from .utils import fsm

# Borrowed from Tomatoro create by Pierre Quillery.
# https://github.com/dandelionmood/Tomatoro
# Thanks Pierre!
ONE_SECOND = 1


class EventPayload(namedtuple("TimerPayload", "time_left duration")):
    __slots__ = ()

    @property
    def ratio(self) -> float:
        try:
            ratio = round(1.0 - self.time_left / self.duration, 1)

        except ZeroDivisionError:
            ratio = 0

        return ratio


@register.factory("tomate.timer", scope=SingletonScope)
class Timer(object):
    @inject(dispatcher="tomate.events.timer")
    def __init__(self, dispatcher):
        self.duration = self.time_left = 0
        self._dispatcher = dispatcher

    @fsm(target=State.started, source=[State.finished, State.stopped])
    def start(self, seconds: int) -> bool:
        self.duration = self.time_left = seconds

        GLib.timeout_add_seconds(ONE_SECOND, self._update)

        return True

    @fsm(target=State.stopped, source=[State.started])
    def stop(self) -> bool:
        self._reset()

        return True

    def timer_is_up(self) -> bool:
        return self.time_left <= 0

    @fsm(target=State.finished, source=[State.started], conditions=[timer_is_up])
    def end(self) -> bool:
        return True

    def _update(self) -> bool:
        if self.state != State.started:
            return False

        if self.timer_is_up():
            return self.end()

        self.time_left -= 1

        self._trigger(State.changed)

        return True

    def _trigger(self, event_type) -> None:
        payload = EventPayload(time_left=self.time_left, duration=self.duration)

        self._dispatcher.send(event_type, payload=payload)

    def _reset(self) -> None:
        self.duration = self.time_left = 0

    state = ObservableProperty(initial=State.stopped, callback=_trigger)
