import functools
import logging
from blinker import Namespace
from wiring.scanning import register

logger = logging.getLogger(__name__)


class Dispatcher(Namespace):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)


Events = Dispatcher()
Session = Events.signal("Session")
Timer = Events.signal("Timer")
Setting = Events.signal("Setting")
View = Events.signal("View")


def on(event, senders):
    def wrapper(func):
        if not hasattr(func, "_has_event"):
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
    methods = [
        getattr(obj, attr)
        for attr in dir(obj)
        if getattr(getattr(obj, attr), "_has_event", False) is True
    ]
    return methods


def connect_events(obj):
    for method in methods_with_events(obj):
        for (event, sender) in method._events:
            logger.debug(
                "Connecting {event} to method {method} with sender {sender}".format(
                    **locals()
                )
            )
            event.connect(method, sender=sender, weak=False)


def disconnect_events(obj):
    for method in methods_with_events(obj):
        for (event, sender) in method._events:
            logger.debug(
                "Disconnecting {event} to method {method} with sender {sender}".format(
                    **locals()
                )
            )
            event.disconnect(method, sender=sender)


class SubscriberMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        connect_events(obj)
        return obj


class Subscriber(metaclass=SubscriberMeta):
    pass


class ObservableProperty(object):
    def __init__(self, initial, callback, attr="_state", event=None):
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


register.instance("tomate.events")(Events)
register.instance("tomate.events.session")(Session)
register.instance("tomate.events.timer")(Timer)
register.instance("tomate.events.setting")(Setting)
register.instance("tomate.events.view")(View)
