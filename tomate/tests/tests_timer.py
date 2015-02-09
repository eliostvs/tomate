from __future__ import division, unicode_literals

import unittest

from mock import patch


@patch('tomate.timer.tomate_signals')
class TimerTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.timer import Timer

        self.timer = Timer()

    def test_timer_running(self, *args):
        self.assertFalse(self.timer.running)

        self.timer.start(10)
        self.assertTrue(self.timer.running)

        self.timer.stop()
        self.assertFalse(self.timer.running)

        self.timer.start(10)
        self.timer.finish()
        self.assertFalse(self.timer.running)

    def test_timer_seconds(self, *args):
        self.assertEqual(0, self.timer._Timer__seconds)

        self.timer.start(10)
        self.assertEqual(10, self.timer._Timer__seconds)

        self.timer.stop()
        self.assertEqual(0, self.timer._Timer__seconds)

        self.timer.start(10)
        self.timer.finish()
        self.assertEqual(0, self.timer._Timer__seconds)

    def test_timer_time_left(self, *args):
        self.assertEqual(0, self.timer.time_left)

        self.timer.start(10)
        self.assertEqual(10, self.timer.time_left)

        self.timer.update()
        self.assertEqual(9, self.timer.time_left)

        self.timer.stop()
        self.assertEqual(0, self.timer.time_left)

        self.timer.start(10)
        self.timer.finish()
        self.assertEqual(0, self.timer.time_left)

    def test_timer_ratio(self, *args):
        self.assertEqual(0, self.timer.time_ratio)

        self.timer.start(10)
        self.assertEqual(0, self.timer.time_ratio)

        self.timer.update()
        self.assertEqual(0.1, self.timer.time_ratio)

        self.timer.update()
        self.timer.update()
        self.assertEqual(0.3, self.timer.time_ratio)

    def test_timer_private_update(self, *args):
        self.assertFalse(False, self.timer._Timer__update())

        self.timer.start(2)
        self.assertTrue(self.timer._Timer__update())
        self.assertEqual(1, self.timer.time_left)

        self.timer._Timer__update()

        self.assertFalse(self.timer._Timer__update())
        self.assertEqual(0, self.timer.time_left)
        self.assertFalse(self.timer.running)


@patch('tomate.timer.tomate_signals')
class TestTimerSignals(unittest.TestCase):

    def make_timer(self):
        from tomate.timer import Timer

        return Timer()

    def test_should_emit_time_finished_signal(self, mock_signals):
        timer = self.make_timer()
        timer.start(1)
        timer._Timer__update()
        timer._Timer__update()

        mock_signals.emit.assert_called('timer_finished',
                                        time_left=0,
                                        time_ratio=0)

    def test_should_emit_time_updated_signal(self, mock_signals):
        timer = self.make_timer()
        timer.start(10)
        timer._Timer__update()

        mock_signals.emit.assert_called_once_with('timer_updated',
                                                  time_left=9,
                                                  time_ratio=0.1)
