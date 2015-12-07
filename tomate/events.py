from __future__ import unicode_literals

import functools
import logging

import six
from blinker import Namespace
from wiring import Module

logger = logging.getLogger(__name__)


class Dispatcher(Namespace):

    def __getattr__(self, attr):
        return self[attr]



Events = Dispatcher()
Session = Events.signal('Session')
Timer = Events.signal('Timer')
Setting = Events.signal('Setting')
View = Events.signal('View')


class SubscriberMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)

        for method in cls.__get_binds(obj):
            (event, sender) = method._bind
            event.connect(method, sender=sender, weak=False)

        return obj

    def __get_binds(self, obj):
        binds = [getattr(obj, attr)
                 for attr in dir(obj)
                 if getattr(getattr(obj, attr), '_is_bind', False) is True]
        return binds


class Subscriber(six.with_metaclass(SubscriberMeta, object)):
    pass


def on(event, sender):
    def wrapper(func):
        func._is_bind = True
        func._bind = (event, sender)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped
    return wrapper


class EventState(object):

    def __init__(self, initial, callback, attr='_state', event_type=None):
        self.initial = initial
        self.callback = callback
        self.state_attr = attr
        self.event_type = event_type

    def __get__(self, instance, owner):
        if instance is None or not hasattr(instance, self.state_attr):
            value = self.initial

        else:
            value = getattr(instance, self.state_attr)

        return value

    def __set__(self, instance, value):
        setattr(instance, self.state_attr, value)
        event = value if self.event_type is None else self.event_type
        self.callback(instance, event)


class EventsModule(Module):

    instances = {
        'tomate.events': Events
    }
