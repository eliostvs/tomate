from __future__ import division, unicode_literals

from gi.repository import GObject
from wiring import inject, Module, SingletonScope

from .constant import State
from .event import EventState
from .utils import fsm

# Borrowed from Tomatoro create by Pierre Quillery.
# https://github.com/dandelionmood/Tomatoro
# Thanks Pierre!


class Timer(object):

    @inject(events='tomate.events')
    def __init__(self, events):
        self.__seconds = self.time_left = 0
        self.event = events.Timer

    @fsm(target=State.started,
         source=[State.finished, State.stopped])
    def start(self, seconds):
        self.__seconds = self.time_left = seconds

        GObject.timeout_add(1000, self._update)

        return True

    @fsm(target=State.stopped,
         source=[State.started])
    def stop(self):
        self._reset()

        return True

    def timer_is_up(self):
        return self.time_left <= 0

    @fsm(target=State.finished,
         source=[State.started],
         conditions=[timer_is_up])
    def end(self):
        self._reset()

        return True

    @property
    def time_ratio(self):
        try:
            ratio = round(1.0 - self.time_left / self.__seconds, 1)

        except ZeroDivisionError:
            ratio = 0

        return ratio

    def _update(self):
        if self.state != State.started:
            return False

        if self.time_left <= 0:
            return self.end()

        self.time_left -= 1

        self._trigger(State.changed)

        return True

    def _trigger(self, event_type):
        self.event.send(event_type,
                        time_left=self.time_left,
                        time_ratio=self.time_ratio)

    def _reset(self):
        self.__seconds = self.time_left = 0

    state = EventState(initial=State.stopped, callback=_trigger)


class TimerModule(Module):

    factories = {
        'tomate.timer': (Timer, SingletonScope),
    }
