from __future__ import unicode_literals

import unittest

from mock import patch


class ConnectSignalMixinTestCase(unittest.TestCase):

    def make_dummy(self):
        from tomate.signals import ConnectSignalMixin

        class Dummy(ConnectSignalMixin):
            signals = (
                ('updated_timer', 'foo'),
            )

            def foo(self):
                pass

        return Dummy()

    @patch('tomate.signals.Dispatcher.connect')
    def test_connect_signal(self, mconnect):
        dummy = self.make_dummy()
        dummy.connect_signals()

        mconnect.assert_called_once_with('updated_timer', dummy.foo)

    @patch('tomate.signals.Dispatcher.disconnect')
    def test_disconnect_signal(self, mdisconnect):
        dummy = self.make_dummy()
        dummy.disconnect_signals()

        mdisconnect.assert_called_once_with('updated_timer', dummy.foo)


@patch('blinker.base.NamedSignal')
class DispatcherTestCase(unittest.TestCase):

    def make_namespace(self):
        from tomate.dispatcher import Dispatcher

        namespace = Dispatcher()
        namespace.signal('test')

        return namespace

    def test_emit_signal(self, mNamedSignal):
        namespace = self.make_namespace()

        mNamedSignal.assert_called_once_with('test', None)

        namespace.emit('test', a=1)

        mNamedSignal.return_value.send.assert_called_once_with(a=1)

    def test_connect_signal(self, mNamedSignal):
        namespace = self.make_namespace()

        def function(): pass

        namespace.connect('test', function)

        mNamedSignal.return_value.connect.assert_called_once_with(function, weak=True)

    def test_disconnect_signal(self, mNamedSignal):
        namespace = self.make_namespace()

        def function(): pass

        namespace.disconnect('test', function)

        mNamedSignal.return_value.disconnect.assert_called_once_with(function)
