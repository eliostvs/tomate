from __future__ import unicode_literals

from wiring import Module, provides, scope, SingletonScope
from yapsy.IPlugin import IPlugin
from yapsy.PluginManagerDecorator import PluginManagerDecorator

from .signals import Subscriber


class InjectablePluginManager(PluginManagerDecorator):

    def __init__(self, decorated_manager=None):
        super(InjectablePluginManager, self).__init__(decorated_manager)
        self._graph = None

    def loadPlugins(self, callback=None):
        processed_plugins = self._component.loadPlugins(callback)

        for plugin in processed_plugins:
            plugin.plugin_object.graph = self._graph

        return processed_plugins

    def setGraph(self, graph):
        self._graph = graph


class Plugin(Subscriber, IPlugin):

    def activate(self):
        super(Plugin, self).activate()
        self.connect()

    def deactivate(self):
        super(Plugin, self).deactivate()
        self.disconnect()


class PluginProvider(Module):

    @provides('tomate.plugin')
    @scope(SingletonScope)
    def create_plugin_manager(self):
        from tomate.graph import graph
        from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
        from yapsy.PluginManager import PluginManagerSingleton
        from yapsy.VersionedPluginManager import VersionedPluginManager

        PluginManagerSingleton.setBehaviour([
            InjectablePluginManager,
            ConfigurablePluginManager,
            VersionedPluginManager,
        ])

        manager = PluginManagerSingleton.get()
        manager.setGraph(graph)
        return manager
