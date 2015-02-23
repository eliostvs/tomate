from __future__ import unicode_literals

import logging
from functools import partial

import dbus.service
from wiring import inject
from wiring.interface import implements, Interface
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.VersionedPluginManager import VersionedPluginManager

from .enums import State
from .plugin import TomatePluginManager
from .utils import suppress_errors

logger = logging.getLogger(__name__)


class IApplication(Interface):

    state = ''
    bus_name = ''
    bus_object_path = ''
    bus_interface_name = ''
    plugin_ext = ''
    pluign_manager_classes = ''

    def is_running():
        pass

    def run():
        pass

    def quit():
        pass


@implements(IApplication)
class Application(dbus.service.Object):

    bus_name = 'com.github.Tomate'
    bus_object_path = '/'
    bus_interface_name = 'com.github.Tomate'
    plugin_ext = 'plugin'
    plugin_manager_classes = (TomatePluginManager,
                              VersionedPluginManager,
                              ConfigurablePluginManager,)

    dbus_method = partial(dbus.service.method,
                          bus_interface_name,
                          in_signature='',
                          out_signature='')

    @inject(session='session', bus='bus_session', profile='profile', view='view')
    def __init__(self, session=None, profile=None, view=None, bus=None):
        dbus.service.Object.__init__(self, bus, self.bus_object_path)

        self.state = State.stopped
        self.profile = profile
        self.session = session
        self.view = view
        self.plugin = self.initialize_plugin()

    @suppress_errors
    def initialize_plugin(self):
        PluginManagerSingleton.setBehaviour(self.plugin_manager_classes)

        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces(self.profile.get_plugin_paths())
        manager.setPluginInfoExtension(self.plugin_ext)
        manager.setApplication(self)
        manager.setConfigParser(self.profile.config_parser,
                                self.profile.save)
        manager.collectPlugins()

        return manager

    @dbus_method(out_signature='b')
    def is_running(self):
        return self.state == State.running

    @dbus_method()
    def run(self):
        if self.is_running():
            self.show()

        else:
            self.state = State.running
            self.session.change_task()
            self.view.run()
            self.state = State.stopped

        return True

    @dbus_method(out_signature='b')
    def quit(self):
        if self.session.timer_is_running():
            return self.view.hide()

        else:
            return self.view.quit()


def application_factory(application_class, view_class, **kwargs):
    bus_session = dbus.SessionBus()
    request = bus_session.request_name(application_class.bus_name,
                                       dbus.bus.NAME_FLAG_DO_NOT_QUEUE)

    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        app = application_class(view_class, bus_session, **kwargs)

    else:
        bus_object = bus_session.get_object(application_class.bus_name,
                                            application_class.bus_object_path)

        app = dbus.Interface(bus_object,
                             application_class.bus_interface_name)

    return app
