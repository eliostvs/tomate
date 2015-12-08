from __future__ import unicode_literals

from wiring import inject, Module, SingletonScope

from .constant import State, Task
from .event import EventState, Subscriber, on, Events
from .utils import fsm


class Session(Subscriber):

    @inject(timer='tomate.timer', config='tomate.config', events='tomate.events')
    def __init__(self, timer, config, events):
        self.config = config
        self.timer = timer
        self.event = events.Session

    def timer_is_running(self):
        return self.timer.state == State.started

    def timer_is_not_running(self):
        return not self.timer_is_running()

    @fsm(target=State.started,
         source=[State.stopped, State.finished])
    def start(self):
        self.timer.start(self.duration)

        return True

    @fsm(target=State.stopped,
         source=[State.started],
         conditions=[timer_is_running])
    def stop(self):
        self.timer.stop()

        return True

    @fsm(target=State.stopped,
         source=[State.stopped, State.finished],
         exit=lambda i: i.trigger(State.reset))
    def reset(self):
        self.count = 0

        return True

    @fsm(target=State.finished,
         source=[State.started],
         conditions=[timer_is_not_running])
    @on(Events.Timer, [State.finished])
    def end(self, sender=None, **kwargs):
        if self.task == Task.pomodoro:
            self.count += 1

            if self.count % self.config.get_int('Timer', 'Long Break Interval'):
                self.task = Task.shortbreak

            else:
                self.task = Task.longbreak

        else:
            self.task = Task.pomodoro

        return True

    @fsm(target=State.stopped,
         source=[State.stopped, State.finished])
    @on(Events.Setting, ['timer'])
    def change_task(self, *args, **kwargs):
        self.task = kwargs.get('task', self.task)

        return True

    @property
    def duration(self):
        option_name = self.task.name + '_duration'
        minutes = self.config.get_int('Timer', option_name)
        return minutes * 60

    def status(self):
        return dict(task=self.task,
                    sessions=self.count,
                    state=self.state,
                    time_left=self.duration)

    def trigger(self, event_type):
        self.event.send(event_type, **self.status())

    state = EventState(State.stopped, trigger)
    count = EventState(0, trigger, attr='_count', event_type=State.changed)
    task = EventState(Task.pomodoro, trigger, attr='_task', event_type=State.changed)


class SessionModule(Module):

    factories = {
        'tomate.session': (Session, SingletonScope)
    }
