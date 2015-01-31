from __future__ import unicode_literals

import enum
from tomate.signals import ConnectSignalMixin

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


class Pomodoro(ConnectSignalMixin):

    state = 'stopped'

    signals = (
        ('timer_finished', 'end'),
        ('start_session', 'start'),
        ('interrupt_session', 'interrupt'),
        ('reset_sessions', 'reset'),
        ('change_task', 'change_task'),
    )

    def __init__(self, *args, **kwargs):
        super(Pomodoro, self).__init__(*args, **kwargs)

        self._timer = Timer()

        self.sessions = 0

        self.task = Task.pomodoro

        self.profile = ProfileManagerSingleton.get()

        self.connect_signals()

    def is_running(self):
        return self._timer.running

    def is_stopped(self):
        return not self.is_running()

    @fsm(target='running', source=['stopped'],
         exit=lambda s: s.emit('session_started'))
    def start(self, sender=None, **kwargs):
        self._timer.start(self.seconds_left)

        return True

    @fsm(target='stopped', source=['running'],
         conditions=[is_running],
         exit=lambda s: s.emit('session_interrupted'))
    def interrupt(self, sender=None, **kwargs):
        self._timer.stop()

        return True

    @fsm(target='stopped', source=['stopped'])
    def reset(self, sender=None, **kwargs):
        self.sessions = 0

        self.emit('sessions_reseted')

        return True

    @fsm(target='stopped', source=['running'],
         conditions=[is_stopped],
         exit=lambda s: s.emit('session_ended'))
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

        self.emit('task_changed')

        return True

    @property
    def seconds_left(self):
        option_name = self.task.name + '_duration'
        minutes = self.profile.get_int('Timer', option_name)
        return minutes * 60

    def emit(self, signal):
        tomate_signals.emit(
            signal,
            task=self.task,
            sessions=self.sessions,
            time_left=self.seconds_left)
