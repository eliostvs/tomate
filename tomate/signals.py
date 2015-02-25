from __future__ import unicode_literals

from blinker import Namespace
from wiring import Module


class TomateNamespace(Namespace):

    def emit(self, name, **kwargs):
        signal = self[name]
        return signal.send(**kwargs)

    def connect(self, name, method):
        signal = self[name]
        signal.connect(method, weak=True)

    def disconnect(self, name, method):
        signal = self[name]
        signal.disconnect(method)


tomate_signals = TomateNamespace()

# Timer
timer_updated = tomate_signals.signal('timer_updated')
timer_finished = tomate_signals.signal('timer_finished')

# Pomodoro
session_started = tomate_signals.signal('session_started')
sessions_reseted = tomate_signals.signal('sessions_reseted')
session_interrupted = tomate_signals.signal('session_interrupted')
session_ended = tomate_signals.signal('session_ended')
task_changed = tomate_signals.signal('task_changed')

# Window
window_showed = tomate_signals.signal('window_showed')
window_hid = tomate_signals.signal('window_hid')

# Settings
setting_changed = tomate_signals.signal('setting_changed')


class SignalsProvider(Module):

    instances = {
        'tomate.signals': tomate_signals
    }
