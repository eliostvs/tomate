from __future__ import unicode_literals

import functools
import logging

logger = logging.getLogger(__name__)


def setup_logging(options):
    fmt = '%(levelname)s:%(asctime)s:%(name)s:%(message)s'

    if options.verbose:
        level = logging.DEBUG

    else:
        level = logging.INFO

    logging.basicConfig(level=level, format=fmt)


def format_time_left(seconds):
    minutes, seconds = divmod(seconds, 60)
    return '{0:0>2}:{1:0>2}'.format(minutes, seconds)


def suppress_errors(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except Exception as e:
            logger = logging.getLogger(function.__module__)
            logger.error(e, exc_info=True)

    return wrapper


class fsm(object):

    def __init__(self, target, **kwargs):
        self.target = target
        self.source = kwargs.pop('source', '*')
        self.attr = kwargs.pop('attr', 'state')
        self.conditions = kwargs.pop('conditions', [])
        self.exit_action = kwargs.pop('exit', None)

    def valid_transition(self, instance):
        if self.source == '*' or getattr(instance, self.attr) in self.source:
            return True

    def valid_conditions(self, instance):
        if not self.conditions:
            return True

        else:
            return all(map(lambda condition: condition(instance), self.conditions))

    def change_state(self, instance):
        setattr(instance, self.attr, self.target)

    def call_exit_action(self, instance):
        if self.exit_action is not None:
            self.exit_action(instance)

    def __call__(self, method):
        @functools.wraps(method)
        def _wrapped(instance, *args, **kwargs):
            if self.valid_transition(instance) and self.valid_conditions(instance):
                result = method(instance, *args, **kwargs)

                self.change_state(instance)

                self.call_exit_action(instance)

                return result

        return _wrapped
