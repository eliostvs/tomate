from __future__ import division, unicode_literals

import unittest

from mock import Mock
from wiring import FactoryProvider, SingletonScope

from tomate.enums import State
from tomate.graph import graph
from tomate.timer import Timer, TimerModule


class TimerTest(unittest.TestCase):

    def setUp(self):
        self.timer = Timer(events=Mock())

    def test_default_timer_values(self):
        print self.timer.state
        self.assertEqual(State.stopped, self.timer.state)
        self.assertEqual(0, self.timer.time_ratio)
        self.assertEqual(0, self.timer.time_left)

    def test_should_not_be_able_to_stop(self):
        self.assertFalse(self.timer.stop())

    def test_should_be_able_to_stop(self):
        self.timer.state = State.running

        self.assertTrue(self.timer.stop())
        self.assertEqual(State.stopped, self.timer.state)

    def test_not_be_able_to_start(self):
        self.timer.state = State.running
        self.assertFalse(self.timer.start(1))

    def test_should_be_able_to_start(self):
        self.timer.state = State.stopped
        self.assertTrue(self.timer.start(1))

        self.timer.state = State.finished
        self.assertTrue(self.timer.start(1))

    def test_should_update_seconds_when_start(self):
        self.timer.state = State.finished

        self.timer.start(1)

        self.assertEqual(1, self.timer.time_left)
        self.assertEqual(1, self.timer._Timer__seconds)

    def test_should_increase_the_time_ratio_after_update(self):
        self.assertEqual(0, self.timer.time_ratio)

        self.timer.start(10)

        self.timer.update()
        self.timer.update()
        self.timer.update()

        self.assertEqual(0.3, self.timer.time_ratio)

    def test_should_decrease_the_time_left_after_update(self):
        self.assertFalse(False, self.timer.update())

        self.timer.start(2)

        self.assertTrue(self.timer.update())
        self.assertEqual(1, self.timer.time_left)

    def test_should_finished_when_the_time_ends(self):
        self.timer.start(1)

        self.timer.update()
        self.timer.update()

        self.assertEqual(State.finished, self.timer.state)

    def test_should_trigger_finished_event(self):
        self.timer.start(1)

        self.timer.update()
        self.timer.update()

        self.timer.event.send.assert_called_with(State.finished, time_left=0, time_ratio=0)

    def test_should_trigger_changed_event(self):
        self.timer.start(10)

        self.timer.update()

        self.timer.event.send.assert_called_with(State.changed, time_left=9, time_ratio=0.1)


class TimerProviderTest(unittest.TestCase):

    def test_module(self):
        self.assertEqual(['tomate.timer'], TimerModule.providers.keys())
        TimerModule().add_to(graph)

        provider = graph.providers['tomate.timer']

        self.assertIsInstance(provider, FactoryProvider)
        self.assertEqual(provider.scope, SingletonScope)
        self.assertEqual(provider.dependencies, {'events': 'tomate.events'})

        graph.register_instance('tomate.events', Mock())
        self.assertIsInstance(graph.get('tomate.timer'), Timer)
