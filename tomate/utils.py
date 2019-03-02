import logging
import os

import wrapt

logger = logging.getLogger(__name__)


def format_time_left(seconds):
    minutes, seconds = divmod(seconds, 60)
    return "{0:0>2}:{1:0>2}".format(minutes, seconds)


def in_debug_mode():
    return "TOMATE_DEBUG" in os.environ.keys()


@wrapt.decorator
def suppress_errors(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)

    except Exception as ex:
        if in_debug_mode():
            raise ex

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
        self.source = kwargs.pop("source", "*")
        self.attr = kwargs.pop("attr", "state")
        self.conditions = kwargs.pop("conditions", [])
        self.exit_action = kwargs.pop("exit", None)

    def valid_transition(self, instance):
        if self.source == "*" or getattr(instance, self.attr) in self.source:
            logger.debug("action=valid_transition result=true")
            return True

        logger.debug("action=valid_transition result=false")

    def valid_conditions(self, instance):
        if not self.conditions:
            return True

        else:
            return all(map(lambda condition: condition(instance), self.conditions))

    def change_state(self, instance):
        current_target = getattr(instance, self.attr, None)

        logger.debug(
            "action=change instance=%s attr=%s from=%s to=%s",
            instance.__class__.__name__,
            self.attr,
            current_target,
            self.target,
        )

        if self.target != "self" and current_target != self.target:
            setattr(instance, self.attr, self.target)

    def call_exit_action(self, instance):
        if self.exit_action is not None:
            self.exit_action(instance)

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        logger.debug(
            "action=beforeCall instance=%s method=%s",
            instance.__class__.__name__,
            wrapped.__name__,
        )

        if self.valid_transition(instance) and self.valid_conditions(instance):
            result = wrapped(*args, **kwargs)

            self.change_state(instance)

            self.call_exit_action(instance)

            logger.debug("action=call result=true")

            return result

        logger.debug("action=call result=false")

        return False
