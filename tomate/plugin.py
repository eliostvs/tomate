from __future__ import unicode_literals

from tomate.base import ConnectSignalMixin
from yapsy.IPlugin import IPlugin
from yapsy.PluginManagerDecorator import PluginManagerDecorator


class AddViewInstancePluginManager(PluginManagerDecorator):

    def __init__(self,
                 decorated_manager=None,
                 categories_filter={'Default': IPlugin},
                 directories_list=None,
                 plugin_info_ext=None,
                 view_instance=None):

        PluginManagerDecorator.__init__(self,
                                        decorated_manager,
                                        categories_filter,
                                        directories_list,
                                        plugin_info_ext)

        self.setViewInstance(view_instance)

    def loadPlugins(self, callback=None):
        processed_plugins = self._component.loadPlugins(callback)

        for plugin in processed_plugins:
            plugin.plugin_object.view = self.view_instance

        return processed_plugins

    def setViewInstance(self, view_instance):
        self.view_instance = view_instance


class TomatePlugin(ConnectSignalMixin, IPlugin):

    def activate(self):
        super(TomatePlugin, self).activate()
        self.connect_signals()

    def deactivate(self):
        super(TomatePlugin, self).deactivate()
        self.disconnect_signals()
