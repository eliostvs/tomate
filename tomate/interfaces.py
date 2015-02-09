from __future__ import unicode_literals


class IView(object):

    def run(self):
        pass

    def quit(self):
        pass

    def show(self):
        pass

    def hide(self):
        pass


class IApplication(IView):

    def start(self):
        pass

    def interrupt(self):
        pass

    def reset(self):
        pass

    def change_task(self):
        pass

    def status(self):
        pass
