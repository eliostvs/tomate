from __future__ import unicode_literals

from tomate.base import ConnectSignalMixin
from yapsy.IPlugin import IPlugin
from yapsy.PluginManagerDecorator import PluginManagerDecorator


class AddViewPluginManager(PluginManagerDecorator):

    def __init__(self,
                 decorated_manager=None,
                 categories_filter={'Default': IPlugin},
                 directories_list=None,
                 plugin_info_ext=None,
                 view=None):

        PluginManagerDecorator.__init__(self,
                                        decorated_manager,
                                        categories_filter,
                                        directories_list,
                                        plugin_info_ext)

        self.setView(view)

    def loadPlugins(self, callback=None):
        processed_plugins = self._component.loadPlugins(callback)

        for plugin in processed_plugins:
            plugin.plugin_object.view = self._view

        return processed_plugins

    def setView(self, view):
        self._view = view


class TomatePlugin(ConnectSignalMixin, IPlugin):

    def __init__(self):
        super(TomatePlugin, self).__init__()

        self.initialize()

    def initialize(self):
        pass

    def activate(self):
        super(TomatePlugin, self).activate()
        self.connect_signals()

    def deactivate(self):
        super(TomatePlugin, self).deactivate()
        self.disconnect_signals()
