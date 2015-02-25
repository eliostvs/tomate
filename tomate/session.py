from __future__ import unicode_literals

from wiring import implements, inject, Interface, Module, SingletonScope

from .enums import State, Task
from .mixins import ConnectSignalMixin
from .utils import fsm


class ISession(Interface):

    state = ''
    duration = ''

    def start():
        pass

    def interrupt():
        pass

    def end():
        pass

    def change_task(task=None):
        pass

    def status():
        pass


@implements(ISession)
class Session(ConnectSignalMixin):

    signals = (
        ('timer_finished', 'end'),
    )

    @inject(timer='tomate.timer', profile='tomate.profile', signals='tomate.signals')
    def __init__(self, timer=None, profile=None, signals=None):
        super(Session, self).__init__()

        self.count = 0
        self.profile = profile
        self.state = State.stopped
        self.task = Task.pomodoro
        self.timer = timer
        self.tomate_signals = signals

        self.connect_signals()

    def timer_is_running(self):
        return self.timer.state == State.running

    def timer_is_not_running(self):
        return not self.timer_is_running()

    @fsm(target=State.running,
         source=[State.stopped],
         exit=lambda s: s.emit('session_started'))
    def start(self):
        self.timer.start(self.duration)

        return True

    @fsm(target=State.stopped,
         source=[State.running],
         conditions=[timer_is_running],
         exit=lambda s: s.emit('session_interrupted'))
    def interrupt(self):
        self.timer.stop()

        return True

    @fsm(target=State.stopped,
         source=[State.stopped],
         exit=lambda s: s.emit('sessions_reseted'))
    def reset(self):
        self.count = 0

        return True

    @fsm(target=State.stopped,
         source=[State.running],
         conditions=[timer_is_not_running],
         exit=lambda s: s.emit('session_ended'))
    def end(self):
        if self.task == Task.pomodoro:
            self.count += 1

            if self.count % self.profile.get_int('Timer', 'Long Break Interval'):
                self.task = Task.shortbreak

            else:
                self.task = Task.longbreak

        else:
            self.task = Task.pomodoro

        return True

    @fsm(target=State.stopped,
         source=[State.stopped],
         exit=lambda s: s.emit('task_changed'))
    def change_task(self, task=None):
        if task is not None:
            self.task = task

        return True

    @property
    def duration(self):
        option_name = self.task.name + '_duration'
        minutes = self.profile.get_int('Timer', option_name)
        return minutes * 60

    def status(self):
        return dict(task=self.task,
                    sessions=self.count,
                    state=self.state,
                    time_left=self.duration)

    def emit(self, name):
        self.tomate_signals.emit(name, **self.status())


class SessionModule(Module):

    factories = {
        'tomate.session': (Session, SingletonScope)
    }
