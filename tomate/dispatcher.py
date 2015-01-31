from __future__ import unicode_literals

from blinker import Namespace


class Dispatcher(Namespace):

    def emit(self, name, **kwargs):
        signal = self[name]
        return signal.send(**kwargs)

    def connect(self, name, method):
        signal = self[name]
        signal.connect(method, weak=True)

    def disconnect(self, name, method):
        signal = self[name]
        signal.disconnect(method)
