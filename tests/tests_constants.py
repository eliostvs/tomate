from __future__ import unicode_literals

import unittest
from tomate.constants import Task


class PomodoroTaskTestCase(unittest.TestCase):

    def test_get_task_by_index(self):
        self.assertEqual(Task.pomodoro, Task.get_by_index(0))
