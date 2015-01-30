from __future__ import division, unicode_literals

from gi.repository import GObject

from .signals import tomate_signals

# Borrowed from Tomatoro create by Pierre Quillery.
# https://github.com/dandelionmood/Tomatoro
# Thanks Pierre!


class Timer(object):

    def __init__(self):
        self.running = False
        self.__seconds = self.time_left = 0

    def start(self, seconds):
        self.running = True
        self.__seconds = self.time_left = seconds

        GObject.timeout_add(1000, self.__update)

    def __update(self):
        '''Timer loop.

        Method executed every second to update the counter.
        '''
        if not self.running:
            return False

        if self.time_left <= 0:
            return self.finish()

        return self.update()

    def update(self):
        self.time_left -= 1

        self.emit('timer_updated')

        return True

    def finish(self):
        self.stop()

        self.emit('timer_finished')

        return False

    def stop(self):
        self.running = False
        self.__seconds = self.time_left = 0

        return False

    @property
    def time_ratio(self):
        try:
            ratio = round(1.0 - self.time_left / self.__seconds, 1)

        except ZeroDivisionError:
            ratio = 0

        return ratio

    def emit(self, signal_name):
        tomate_signals[signal_name].send(
            self.__class__,
            time_left=self.time_left,
            time_ratio=self.time_ratio)
