from __future__ import unicode_literals

import unittest
from tomate.enums import Base


class BaseTest(unittest.TestCase):

    def test_get_task_by_index(self):
        class Dummy(Base):
            a = 1
            b = 2
        
        self.assertEqual(Dummy.a, Dummy.by_index(0))
        self.assertEqual(Dummy.b, Dummy.by_index(1))
