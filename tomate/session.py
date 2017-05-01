from __future__ import unicode_literals

from wiring import inject, SingletonScope
from wiring.scanning import register

from .constant import State, Task
from .event import EventState, Subscriber, on, Events
from .utils import fsm


@register.factory('tomate.session', scope=SingletonScope)
class Session(Subscriber):
    @inject(timer='tomate.timer', config='tomate.config', event='tomate.events.session')
    def __init__(self, timer, config, event):
        self.config = config
        self.timer = timer
        self.event = event

    def is_running(self):
        return self.timer.state == State.started

    def is_not_running(self):
        return not self.is_running()

    @fsm(target=State.started,
         source=[State.stopped, State.finished])
    def start(self):
        self.timer.start(self.duration)

        return True

    @fsm(target=State.stopped,
         source=[State.started],
         conditions=[is_running])
    def stop(self):
        self.timer.stop()

        return True

    @fsm(target='self',
         source=[State.stopped, State.finished],
         exit=lambda self: self._trigger(State.reset))
    def reset(self):
        self.count = 0

        return True

    @fsm(target=State.finished,
         source=[State.started],
         conditions=[is_not_running])
    @on(Events.Timer, [State.finished])
    def end(self, sender=None, **kwargs):
        if self.current_task_is(Task.pomodoro):
            self.count += 1
            self.task = (Task.longbreak
                         if self._is_time_to_long_break
                         else Task.shortbreak)

        else:
            self.task = Task.pomodoro

        return True

    @fsm(target='self',
         source=[State.stopped, State.finished])
    @on(Events.Setting, ['timer'])
    def change_task(self, sender=None, **kwargs):
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

    def current_task_is(self, task_type):
        return self.task == task_type

    def _trigger(self, event_type):
        self.event.send(event_type, **self.status())

    @property
    def _is_time_to_long_break(self):
        return not self.count % self.config.get_int('Timer', 'Long Break Interval')

    state = EventState(initial=State.stopped, callback=_trigger)

    count = EventState(initial=0,
                       callback=_trigger,
                       attr='_count',
                       event=State.changed)

    task = EventState(initial=Task.pomodoro,
                      callback=_trigger,
                      attr='_task',
                      event=State.changed)
