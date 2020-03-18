import contextlib
import dbus
import pytest

from tomate.constant import State


@pytest.fixture()
def subject(mocker, mock_view, mock_plugin):
    from tomate.app import Application

    return Application(bus=mocker.Mock(), view=mock_view, plugin=mock_plugin)


def test_from_graph(mocker, graph, mock_plugin, mock_view):
    mocker.patch("tomate.app.dbus.SessionBus")

    from tomate.app import Application

    graph.register_instance("tomate.view", mock_view)
    graph.register_instance("tomate.plugin", mock_plugin)
    graph.register_factory("tomate.app", Application)

    app = Application.from_graph(graph)

    assert isinstance(app, Application)

    with contextlib.ExitStack() as stack:
        stack.enter_context(mocker.patch(
            "tomate.app.dbus.SessionBus.return_value.request_name",
            return_value=dbus.bus.REQUEST_NAME_REPLY_EXISTS,
        ))
        dbus_app = Application.from_graph(graph)

        assert isinstance(dbus_app, dbus.Interface)


def test_run_when_not_running(subject):
    subject.run()

    subject.view.run.assert_called_once_with()


def test_run_when_already_running(subject):
    subject.state = State.started

    subject.run()

    subject.view.show.assert_called_once_with()


def test_is_running(subject):
    assert not subject.is_running()

    subject.state = State.started

    assert subject.is_running()


def test_should_load_plugins_in_init(subject, mock_plugin):
    mock_plugin.collectPlugins()
