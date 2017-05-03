from __future__ import unicode_literals

import logging
import os
import sys

import six
import wrapt

logger = logging.getLogger(__name__)


def format_time_left(seconds):
    minutes, seconds = divmod(seconds, 60)
    return '{0:0>2}:{1:0>2}'.format(minutes, seconds)


def in_debug_mode():
    return 'TOMATE_DEBUG' in os.environ.keys()


@wrapt.decorator
def suppress_errors(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)

    except Exception as ex:
        if in_debug_mode():
            six.reraise(*sys.exc_info())

        log = logging.getLogger(__name__)
        log.error(ex, exc_info=True)

    return None


def rounded_percent(percent):
    """
    The icons show 5% steps, so we have to round.
    """
    return percent - percent % 5


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

        logger.debug('Invalid transition!')

    def valid_conditions(self, instance):
        if not self.conditions:
            return True

        else:
            return all(map(lambda condition: condition(instance), self.conditions))

    def change_state(self, instance):
        logger.debug('Changing %s %s to %s',
                     instance.__class__.__name__, self.attr, self.target)

        if self.target != 'self' and getattr(instance, self.attr, None) != self.target:
            setattr(instance, self.attr, self.target)

    def call_exit_action(self, instance):
        if self.exit_action is not None:
            self.exit_action(instance)

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        logger.debug('Calling %s.%s', instance.__class__.__name__, wrapped)

        if self.valid_transition(instance) and self.valid_conditions(instance):
            result = wrapped(*args, **kwargs)

            self.change_state(instance)

            self.call_exit_action(instance)

            return result

        logger.debug('Invalid conditions!')

        return False
