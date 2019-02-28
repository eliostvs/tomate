import pytest


@pytest.fixture()
def mock_config(mocker):
    from tomate.config import Config

    return mocker.Mock(Config, parser=mocker.Mock(), **{"get_int.return_value": 25})


@pytest.fixture()
def mock_session(mocker):
    from tomate.session import Session

    return mocker.Mock(Session)


@pytest.fixture()
def mock_timer(mocker):
    from tomate.timer import Timer

    return mocker.Mock(Timer)


@pytest.fixture()
def graph():
    from tomate.graph import graph

    graph.providers.clear()

    return graph


@pytest.fixture()
def mock_plugin(mocker):
    from yapsy.PluginManager import PluginManager

    return mocker.Mock(PluginManager)


@pytest.fixture()
def mock_view(mocker):
    return mocker.Mock()
