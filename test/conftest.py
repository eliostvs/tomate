from __future__ import unicode_literals

import pytest
from mock import Mock
from wiring.scanning import scan_to_graph


@pytest.fixture()
def timer():
    from tomate.timer import Timer

    return Timer(event=Mock())


@pytest.fixture()
def session(timer):
    from tomate.session import Session
    from tomate.event import Setting

    Setting.receivers.clear()

    return Session(timer=timer, config=Mock(**{'get_int.return_value': 25}), event=Mock())


@pytest.fixture
def graph():
    from tomate.graph import graph

    scan_to_graph(['tomate'], graph)

    return graph
