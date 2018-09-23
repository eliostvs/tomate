from unittest.mock import Mock
import pytest
from wiring.scanning import scan_to_graph


@pytest.fixture()
def timer():
    from tomate.timer import Timer

    return Timer(dispatcher=Mock())


@pytest.fixture()
def config():
    return Mock(**{'get_int.return_value': 25})


@pytest.fixture()
def session(timer, config):
    from tomate.session import Session
    from tomate.event import Setting

    Setting.receivers.clear()

    return Session(timer=timer, config=config, event=Mock())


@pytest.fixture
def graph():
    from tomate.graph import graph

    graph.providers.clear()

    scan_to_graph(['tomate'], graph)

    return graph
