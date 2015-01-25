import unittest

from mock import patch


class TimerTestCase(unittest.TestCase):

    def setUp(self):
        from tomate.timer import Timer
        self.timer = Timer()

    def test_timer_running(self):
        self.assertFalse(self.timer.running)

        self.timer.start(10)
        self.assertTrue(self.timer.running)

        self.timer.stop()
        self.assertFalse(self.timer.running)

        self.timer.start(10)
        self.timer.finish()
        self.assertFalse(self.timer.running)

    def test_timer_seconds(self):
        self.assertEqual(0, self.timer._Timer__seconds)

        self.timer.start(10)
        self.assertEqual(10, self.timer._Timer__seconds)

        self.timer.stop()
        self.assertEqual(0, self.timer._Timer__seconds)

        self.timer.start(10)
        self.timer.finish()
        self.assertEqual(0, self.timer._Timer__seconds)

    def test_timer_time_left(self):
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

    def test_timer_ratio(self):
        self.assertEqual(0, self.timer.time_ratio)

        self.timer.start(10)
        self.assertEqual(0, self.timer.time_ratio)

        self.timer.update()
        self.assertEqual(0.1, self.timer.time_ratio)

        self.timer.update()
        self.timer.update()
        self.assertEqual(0.3, self.timer.time_ratio)

    def test_timer_private_update(self):
        self.assertFalse(False, self.timer._Timer__update())

        self.timer.start(2)
        self.assertTrue(self.timer._Timer__update())
        self.assertEqual(1, self.timer.time_left)

        self.timer._Timer__update()

        self.assertFalse(self.timer._Timer__update())
        self.assertEqual(0, self.timer.time_left)
        self.assertFalse(self.timer.running)

    @patch('tomate.timer.timer_finished')
    def test_should_emit_time_finished_signal(self, mtimer_finished):
        self.timer.start(1)
        self.timer._Timer__update()
        self.timer._Timer__update()

        self.assertTrue(mtimer_finished.send.called)

        mtimer_finished.send.assert_called_once_with(self.timer.__class__,
                                                     time_left=0,
                                                     time_ratio=0)

    @patch('tomate.timer.timer_updated')
    def test_should_emit_time_updated_signal(self, mtimer_updated):
        self.timer.start(10)
        self.timer._Timer__update()

        self.assertTrue(mtimer_updated.send.called)

        mtimer_updated.send.assert_called_once_with(self.timer.__class__,
                                                    time_left=9,
                                                    time_ratio=0.1)
