from __future__ import unicode_literals

from tomate.mixins import ConnectSignalMixin

from .profile import ProfileManagerSingleton
from .signals import tomate_signals
from .timer import Timer
from .utils import fsm
from .constants import Task


class Pomodoro(ConnectSignalMixin):

    state = 'stopped'

    signals = (
        ('timer_finished', 'end'),
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

    @fsm(target='stopped', source=['stopped'],
         exit=lambda s: s.emit('sessions_reseted'))
    def reset(self, sender=None, **kwargs):
        self.sessions = 0

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

    @fsm(target='stopped', source=['stopped'],
         exit=lambda s: s.emit('task_changed'))
    def change_task(self, *args, **kwargs):
        self.task = kwargs.pop('task', Task.pomodoro)

        return True

    @property
    def seconds_left(self):
        option_name = self.task.name + '_duration'
        minutes = self.profile.get_int('Timer', option_name)
        return minutes * 60

    def emit(self, signal):
        tomate_signals.emit(signal, **self.status)

    @property
    def status(self):
        return dict(task=self.task,
                    sessions=self.sessions,
                    state=self.state,
                    time_left=self.seconds_left)
