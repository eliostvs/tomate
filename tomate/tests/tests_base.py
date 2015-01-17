from __future__ import unicode_literals

import unittest

from mock import patch


@patch('tomate.base.tomate_signals')
class ConnectSignalMixinTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.base import ConnectSignalMixin

        class Dummy(ConnectSignalMixin):
            signals = (
                ('timer_updated', 'foo'),
            )

            def foo(self):
                pass

        self.dummy = Dummy()

    def test_connect_signal(self, mtomate_signals):
        self.dummy.connect_signals()

        signal = mtomate_signals.__getitem__
        signal.assert_called_once_with('timer_updated')
        signal.return_value.connect.assert_called_once_with(self.dummy.foo, weak=False)

    def test_disconnect_signal(self, mtomate_signals):
        self.dummy.disconnect_signals()

        signal = mtomate_signals.__getitem__
        signal.return_value.disconnect.assert_called_once_with(self.dummy.foo)
