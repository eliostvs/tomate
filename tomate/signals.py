from __future__ import unicode_literals

from tomate.dispatcher import Dispatcher

tomate_signals = Dispatcher()

# Timer
timer_updated = tomate_signals.signal('timer_updated')
timer_finished = tomate_signals.signal('timer_finished')

# Pomodoro
session_started = tomate_signals.signal('session_started')
sessions_reseted = tomate_signals.signal('sessions_reseted')
session_interrupted = tomate_signals.signal('session_interrupted')
session_ended = tomate_signals.signal('session_ended')
task_changed = tomate_signals.signal('task_changed')

# Application
app_request = tomate_signals.signal('app_request')

# Window
window_showed = tomate_signals.signal('window_showed')
window_hid = tomate_signals.signal('window_hid')

# Settings
setting_changed = tomate_signals.signal('setting_changed')
