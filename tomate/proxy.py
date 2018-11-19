from wiring import injected, Graph
from wiring.scanning import register


class LazyProxy(object):
    def __init__(self, specification, graph):
        self.__specification = specification
        self.__graph = graph

    def __getattribute__(self, item):
        try:
            obj = object.__getattribute__(self, item)

        except AttributeError:
            target = self.__graph.get(self.__specification)
            obj = object.__getattribute__(target, item)

        return obj


@register.function("tomate.proxy")
def lazy_proxy(specification, graph=injected(Graph)):
    return LazyProxy(specification, graph)
