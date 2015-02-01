from __future__ import unicode_literals

import logging

from tomate.signals import tomate_signals

logger = logging.getLogger(__name__)


class ConnectSignalMixin(object):

    signals = ()

    def connect_signals(self):
        for (signal, method) in self.signals:
            tomate_signals.connect(signal, getattr(self, method))

            logger.debug('method %s.%s connect to signal %s.',
                         self.__class__.__name__, method, signal)

    def disconnect_signals(self):
        for (signal, method) in self.signals:
            tomate_signals.disconnect(signal, getattr(self, method))

            logger.debug('method %s.%s disconnect from signal %s.',
                         self.__class__.__name__, method, signal)
