from __future__ import unicode_literals

import functools
import logging

import six
from blinker import Namespace
from wiring import Module

logger = logging.getLogger(__name__)


class Dispatcher(Namespace):

    def __getattr__(self, attr):
        if attr == '__bases__':  # Prevent yapsy break when a plugin is imported
            return []

        return self[attr]


Events = Dispatcher()
Session = Events.signal('Session')
Timer = Events.signal('Timer')
Setting = Events.signal('Setting')
View = Events.signal('View')


def on(event, senders):
    def wrapper(func):
        if not hasattr(func, '_has_event'):
            func._has_event = True
            func._events = []

        for each in senders:
            func._events.append((event, each))

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped
    return wrapper


def methods_with_events(obj):
    methods = [getattr(obj, attr)
               for attr in dir(obj)
               if getattr(getattr(obj, attr), '_has_event', False) is True]
    return methods


def connect_events(obj):
    for method in methods_with_events(obj):
        for (event, sender) in method._events:
            logger.debug('Connecting {event} to method {method} with sender {sender}'
                         .format(**locals()))
            event.connect(method, sender=sender, weak=False)


def disconnect_events(obj):
    for method in methods_with_events(obj):
        for (event, sender) in method._events:
            logger.debug('Disconnecting {event} to method {method} with sender {sender}'
                         .format(**locals()))
            event.disconnect(method, sender=sender)


class SubscriberMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)

        connect_events(obj)

        return obj


class Subscriber(six.with_metaclass(SubscriberMeta, object)):
    pass


class EventState(object):

    def __init__(self, initial, callback, attr='_state', event=None):
        self.initial = initial
        self.callback = callback
        self.attr = attr
        self.event = event

    def __get__(self, instance, owner):
        if instance is None or not hasattr(instance, self.attr):
            value = self.initial

        else:
            value = getattr(instance, self.attr)

        return value

    def __set__(self, instance, value):
        setattr(instance, self.attr, value)
        event = value if self.event is None else self.event
        self.callback(instance, event)


class EventModule(Module):

    instances = {
        'tomate.events': Events
    }
