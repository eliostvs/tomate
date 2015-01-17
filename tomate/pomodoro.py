from __future__ import unicode_literals

import enum
from tomate.base import ConnectSignalMixin

from .profile import ProfileManagerSingleton
from .signals import tomate_signals
from .timer import Timer
from .utils import fsm


class Task(enum.Enum):
    pomodoro = 0
    shortbreak = 1
    longbreak = 2

    @classmethod
    def get_by_index(cls, index):
        for i, k in enumerate(cls):
            if i == index:
                return k


def _timer_is_running(instance):
    return instance._timer.running


def _timer_is_stopped(instance):
    return not instance._timer.running


def _send_session_ended_signal(instance):
    instance.send_signal('session_ended')


def _send_session_started_signal(instance):
    instance.send_signal('session_started')


def _send_session_interrupt_signal(instance):
    instance.send_signal('session_interrupted')


class Pomodoro(ConnectSignalMixin):

    state = 'stopped'

    signals = (
        ('timer_finished', 'end'),
        ('start_session', 'start'),
        ('interrupt_session', 'interrupt'),
        ('reset_sessions', 'reset'),
        ('change_task', 'change_task'),
    )

    def __init__(self):
        self._timer = Timer()

        self.sessions = 0

        self.task = Task.pomodoro

        self.profile = ProfileManagerSingleton.get()

        self.connect_signals()

    @fsm(target='running', source=['stopped'],
         exit=[_send_session_started_signal])
    def start(self, sender=None, **kwargs):
        self._timer.start(self.session_duration)

        return True

    @fsm(target='stopped', source=['running'],
         conditions=[_timer_is_running],
         exit=[_send_session_interrupt_signal])
    def interrupt(self, sender=None, **kwargs):
        self._timer.stop()

        return True

    @fsm(target='stopped', source=['stopped'])
    def reset(self, sender=None, **kwargs):
        self.sessions = 0

        self.send_signal('sessions_reseted')

        return True

    @fsm(target='stopped', source=['running'],
         conditions=[_timer_is_stopped],
         exit=[_send_session_ended_signal])
    def end(self, sender=None, **kwargs):
        if self.task == Task.pomodoro:
            self.sessions += 1

            if self.sessions % self.profile.get_int('Timer', 'Long Break Interval'):
                self.task = Task.shortbreak

            else:
                self.task = Task.longbreak

        else:
            self.task = Task.pomodoro

        return True

    @fsm(target='stopped', source=['stopped'])
    def change_task(self, sender=None, **kwargs):
        self.task = kwargs.pop('task', Task.pomodoro)

        self.send_signal('task_changed')

        return True

    @property
    def session_duration(self):
        option_name = self.task.name + '_duration'
        minutes = self.profile.get_int('Timer', option_name)
        return minutes * 60

    def send_signal(self, signal_name):
        tomate_signals[signal_name].send(
            self.__class__,
            task=self.task,
            sessions=self.sessions,
            time_left=self.session_duration)
