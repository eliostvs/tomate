from __future__ import unicode_literals

import logging
from functools import partial

import dbus.service
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.VersionedPluginManager import VersionedPluginManager

from .plugin import AddViewPluginManager
from .pomodoro import Pomodoro
from .profile import ProfileManagerSingleton
from .interfaces import IView

logger = logging.getLogger(__name__)


class Application(dbus.service.Object):

    bus_name = 'com.github.Tomate'
    bus_object_path = '/'
    bus_interface_name = 'com.github.Tomate'
    plugin_ext = 'plugin'
    plugin_manager_classes = (AddViewPluginManager,
                              VersionedPluginManager,
                              ConfigurablePluginManager,)
    view_class = None

    dbus_method = partial(dbus.service.method,
                          bus_interface_name,
                          in_signature='',
                          out_signature='')

    def __init__(self, bus, **kwargs):
        dbus.service.Object.__init__(self, bus, self.bus_object_path)

        self.running = False

        self.profile = ProfileManagerSingleton.get()

        self.pomodoro = Pomodoro()

        self.view = self.initialize_view()

        self.plugin = self.initialize_plugin()

    def initialize_view(self):
        if self.view_class is None:
            return IView()

        return self.view_class()

    def initialize_plugin(self):
        PluginManagerSingleton.setBehaviour(self.plugin_manager_classes)

        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces(self.profile.get_plugin_paths())
        manager.setPluginInfoExtension(self.plugin_ext)
        manager.setView(self.view)
        manager.setConfigParser(self.profile.config_parser,
                                self.profile.write_config)
        manager.collectPlugins()

        return manager

    @dbus_method(out_signature='b')
    def is_running(self):
        return self.running

    @dbus_method()
    def run(self, *args, **kwargs):
        if self.running:
            self.view.show()

        else:
            self.running = True
            self.pomodoro.change_task()
            self.view.run()
            self.running = False

    @dbus_method(out_signature='b')
    def quit(self, *args, **kwargs):
        if self.pomodoro.is_running():
            return self.hide()

        else:
            return self.view.quit()

    def hide(self):
        return self.view.hide()

    def show(self):
        return self.view.show()

    def start(self):
        return self.pomodoro.start()

    def interrupt(self):
        return self.pomodoro.interrupt()

    def reset(self):
        return self.pomodoro.reset()

    def change_task(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        return self.pomodoro.change_task(task=task)


def application_factory(application_class, **kwargs):
    bus_session = dbus.SessionBus()
    request = bus_session.request_name(application_class.bus_name,
                                       dbus.bus.NAME_FLAG_DO_NOT_QUEUE)

    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        app = application_class(bus_session, **kwargs)

    else:
        bus_object = bus_session.get_object(application_class.bus_name,
                                            application_class.bus_object_path)

        app = dbus.Interface(bus_object,
                             application_class.bus_interface_name)

    return app
