from gi.repository import GLib
from wiring import inject, SingletonScope
from wiring.scanning import register

from .constant import State
from .event import ObservableProperty
from .utils import fsm

# Borrowed from Tomatoro create by Pierre Quillery.
# https://github.com/dandelionmood/Tomatoro
# Thanks Pierre!
ONE_SECOND = 1000


@register.factory('tomate.timer', scope=SingletonScope)
class Timer(object):
    @inject(dispatcher='tomate.events.timer')
    def __init__(self, dispatcher):
        self.total_seconds = self.seconds_left = 0
        self._dispatcher = dispatcher

    @fsm(target=State.started,
         source=[State.finished, State.stopped])
    def start(self, seconds):
        self.total_seconds = self.seconds_left = seconds

        GLib.timeout_add(ONE_SECOND, self._update)

        return True

    @fsm(target=State.stopped,
         source=[State.started])
    def stop(self):
        self._reset()

        return True

    def timer_is_up(self):
        return self.seconds_left <= 0

    @fsm(target=State.finished,
         source=[State.started],
         conditions=[timer_is_up])
    def end(self):
        self._reset()

        return True

    @property
    def time_ratio(self):
        try:
            ratio = round(1.0 - self.seconds_left / self.total_seconds, 1)

        except ZeroDivisionError:
            ratio = 0

        return ratio

    def _update(self):
        if self.state != State.started:
            return False

        if self.seconds_left <= 0:
            return self.end()

        self.seconds_left -= 1

        self._trigger(State.changed)

        return True

    def _trigger(self, event_type):
        self._dispatcher.send(event_type,
                              time_left=self.seconds_left,
                              time_ratio=self.time_ratio)

    def _reset(self):
        self.total_seconds = self.seconds_left = 0

    state = ObservableProperty(initial=State.stopped, callback=_trigger)
