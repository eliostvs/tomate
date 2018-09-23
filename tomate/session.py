from wiring import inject, SingletonScope
from wiring.scanning import register

from .constant import State, Sessions
from .event import ObservableProperty, Subscriber, on, Events
from .utils import fsm

SECONDS_IN_A_MINUTE = 60


@register.factory('tomate.session', scope=SingletonScope)
class Session(Subscriber):
    @inject(timer='tomate.timer', config='tomate.config', dispatcher='tomate.events.session')
    def __init__(self, timer, config, dispatcher):
        self._config = config
        self._timer = timer
        self._dispatcher = dispatcher
        self.__task_name = ''

    def is_running(self):
        return self._timer.state == State.started

    def is_not_running(self):
        return not self.is_running()

    @fsm(target=State.started,
         source=[State.stopped, State.finished])
    def start(self):
        self._timer.start(self.duration)

        return True

    @fsm(target=State.stopped,
         source=[State.started],
         conditions=[is_running])
    def stop(self):
        self._timer.stop()

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
        if self.current_task_is(Sessions.pomodoro):
            self.count += 1
            self.current = (Sessions.longbreak
                            if self._is_time_to_long_break
                            else Sessions.shortbreak)

        else:
            self.current = Sessions.pomodoro

        return True

    @fsm(target='self',
         source=[State.stopped, State.finished])
    @on(Events.Setting, ['timer'])
    def change_task(self, sender=None, **kwargs):
        self.current = kwargs.get('task', self.current)

        return True

    @property
    def duration(self):
        option_name = self.current.name + '_duration'
        seconds = self._config.get_int('Timer', option_name)
        return seconds * SECONDS_IN_A_MINUTE

    def status(self):
        return dict(
            current=self.current,
            sessions=self.count,
            state=self.state,
            time_left=self.duration,
            task_name=self.task_name)

    def current_task_is(self, session_type):
        return self.current == session_type

    def _trigger(self, event_type):
        self._dispatcher.send(event_type, **self.status())

    @property
    def task_name(self):
        return self.__task_name

    @task_name.setter
    def task_name(self, task_name):
        if self.state in [State.stopped, State.finished]:
            self.__task_name = task_name

    @property
    def _is_time_to_long_break(self):
        return not self.count % self._config.get_int('Timer', 'Long Break Interval')

    state = ObservableProperty(initial=State.stopped, callback=_trigger)

    count = ObservableProperty(initial=0,
                               callback=_trigger,
                               attr='_count',
                               event=State.changed)

    current = ObservableProperty(initial=Sessions.pomodoro,
                                 callback=_trigger,
                                 attr='_current',
                                 event=State.changed)
