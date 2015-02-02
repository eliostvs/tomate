from __future__ import unicode_literals

import enum


@enum.unique
class Task(enum.Enum):
    pomodoro = 0
    shortbreak = 1
    longbreak = 2

    @classmethod
    def get_by_index(cls, index):
        for i, k in enumerate(cls):
            if i == index:
                return k
