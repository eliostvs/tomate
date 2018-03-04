import dbus
import pytest
from mock import Mock, patch
from wiring import Graph

from tomate.constant import State


@pytest.fixture()
def app():
    from tomate.app import Application

    return Application(bus=Mock(), view=Mock(), config=Mock(), plugin=Mock())


@patch('tomate.app.dbus.SessionBus')
def test_the_factory(mock_session_bus=None):
    from tomate.app import Application

    graph = Graph()
    graph.register_factory('tomate.view', Mock)
    graph.register_factory('tomate.config', Mock)
    graph.register_factory('tomate.plugin', Mock)

    graph.register_factory('tomate.app', Application)

    app = Application.from_graph(graph)

    assert isinstance(app, Application)

    with patch('tomate.app.dbus.SessionBus.return_value.request_name',
               return_value=dbus.bus.REQUEST_NAME_REPLY_EXISTS):
        dbus_app = Application.from_graph(graph)

        assert isinstance(dbus_app, dbus.Interface)


def test_run_when_not_running(app):
    app.run()

    app.view.run.assert_called_once_with()


def test_run_when_already_running(app):
    app.state = State.started

    app.run()

    app.view.show.assert_called_once_with()


def test_is_running(app):
    assert not app.is_running()

    app.state = State.started

    assert app.is_running()
