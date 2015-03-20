from __future__ import unicode_literals

from wiring import Interface


class IView(Interface):

    def run(*args, **kwargs):
        pass

    def quit(*args, **kwargs):
        pass

    def show(*args, **kwargs):
        pass

    def hide(*args, **kwargs):
        pass
