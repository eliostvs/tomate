import enum


@enum.unique
class Base(enum.Enum):
    @classmethod
    def by_index(cls, number):
        for (index, attr) in enumerate(cls):
            if index == number:
                return attr


class Sessions(Base):
    pomodoro = 0
    shortbreak = 1
    longbreak = 2


class State(Base):
    stopped = 0
    started = 1
    finished = 3
    changed = 4
    showed = 5
    hid = 6
    reset = 7
