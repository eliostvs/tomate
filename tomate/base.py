from __future__ import unicode_literals

import logging

from tomate.signals import tomate_signals

logger = logging.getLogger(__name__)


class ConnectSignalMixin(object):

    signals = ()

    def connect_signals(self):
        for (signal, method) in self.signals:
            tomate_signals[signal].connect(getattr(self, method), weak=False)

            logger.debug('method %s.%s connect to signal %s.',
                         self.__class__.__name__, method, signal)

    def disconnect_signals(self):
        for (signal, method) in self.signals:
            tomate_signals[signal].disconnect(getattr(self, method))

            logger.debug('method %s.%s disconnect from signal %s.',
                         self.__class__.__name__, method, signal)


class AutoConnectSignalMixin(ConnectSignalMixin):

    def __init__(self):
        super(AutoConnectSignalMixin, self).__init__()

        self.connect_signals()
