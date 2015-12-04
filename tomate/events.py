from __future__ import unicode_literals

import logging

import wrapt
from blinker import Namespace
from wiring import Module

logger = logging.getLogger(__name__)


class TomateNamespace(Namespace):

    def emit(self, name, **kwargs):
        signal = self[name]
        return signal.send(**kwargs)

    def connect(self, name, method):
        signal = self[name]
        signal.connect(method, weak=False)

    def disconnect(self, name, method):
        signal = self[name]
        signal.disconnect(method)


events = TomateNamespace()

# Timer
timer_updated = events.signal('timer_updated')
timer_finished = events.signal('timer_finished')

# Pomodoro
session_started = events.signal('session_started')
sessions_reseted = events.signal('sessions_reseted')
session_interrupted = events.signal('session_interrupted')
session_ended = events.signal('session_ended')
task_changed = events.signal('task_changed')

# Window
view_showed = events.signal('view_showed')
view_hid = events.signal('view_hid')

# Settings
setting_changed = events.signal('setting_changed')


class Subscriber(object):

    subscriptions = ()

    def connect(self):
        for (signal, method) in self.subscriptions:
            events.connect(signal, getattr(self, method))

            logger.debug('method %s.%s connect to signal %s.',
                         self.__class__.__name__, method, signal)

    def disconnect(self):
        for (signal, method) in self.subscriptions:
            events.disconnect(signal, getattr(self, method))

            logger.debug('method %s.%s disconnect from signal %s.',
                         self.__class__.__name__, method, signal)


@wrapt.decorator
def subscribe(wrapped, instance, args, kwargs):
    for (signal, method) in instance.subscriptions:
        events.connect(signal, getattr(instance, method))

        logger.debug('method %s.%s connect to signal %s.',
                     instance.__class__.__name__, method, signal)

    return wrapped(*args, **kwargs)


class SignalsProvider(Module):

    instances = {
        'tomate.events': events
    }
