import pytest
from wiring import SingletonScope
from wiring.scanning import scan_to_graph
from yapsy.VersionedPluginManager import VersionedPluginManager
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager

from tomate.constant import State
from tomate.event import on
from tomate.plugin import Plugin, PluginManager


@pytest.fixture()
def mock_event(mocker):
    return mocker.Mock()


@pytest.fixture()
def plugin(mock_event):
    class Subject(Plugin):
        @on(mock_event, [State.finished])
        def bar(self, sender):
            return sender

    return Subject()


def test_should_disconnect_events_when_plugin_deactivate(plugin, mock_event):
    plugin.deactivate()

    mock_event.disconnect.assert_any_call(plugin.bar, sender=State.finished)


def test_should_connect_events_when_plugin_active(plugin, mock_event):
    plugin.activate()

    mock_event.connect.assert_any_call(plugin.bar, sender=State.finished, weak=False)


def test_should_setup_yapsy_on_init(mock_config, mocker):
    mock_config.get_plugin_paths.return_value = "path"
    factory = mocker.patch("tomate.plugin.PluginManagerSingleton")
    singleton = mocker.Mock()
    factory.get.return_value = singleton

    PluginManager(mock_config)

    factory.setBehaviour.assert_called_once_with(
        [ConfigurablePluginManager, VersionedPluginManager]
    )
    singleton.setPluginPlaces.assert_any_call("path")
    singleton.setPluginInfoExtension.assert_any_call("plugin")
    singleton.setConfigParser.assert_any_call(mock_config.parser, mock_config.save)


def test_should_delegate_to_plugin_manager(mocker, mock_config):
    factory = mocker.patch("tomate.plugin.PluginManagerSingleton")
    singleton = mocker.Mock()
    factory.get.return_value = singleton

    subject = PluginManager(mock_config)

    subject.foo()

    singleton.foo.assert_called_once_with()


def test_module(graph, mock_config):
    spec = "tomate.plugin"

    scan_to_graph([spec], graph)

    assert spec in graph.providers

    provider = graph.providers[spec]

    assert provider.scope == SingletonScope

    graph.register_instance("tomate.config", mock_config)

    assert isinstance(graph.get(spec), PluginManager)
