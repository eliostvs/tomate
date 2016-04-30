from __future__ import unicode_literals

from wiring import injected, Graph, Module


class LazyProxy(object):

    def __init__(self, graph, specification):
        self.__specification = specification
        self.__graph = graph

    def __getattribute__(self, item):
        try:
            obj = object.__getattribute__(self, item)

        except AttributeError:
            obj = object.__getattribute__(self.__target, item)

        return obj

    @property
    def
        return self.__graph.get(self.__specification)


def lazy_proxy(specification, graph=injected(Graph)):
    return LazyProxy(specification, graph)


class ProxyModule(Module):
    functions = {
        'tomate.proxy': lazy_proxy
    }
