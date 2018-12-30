from wiring import Graph

from tomate.proxy import LazyProxy, lazy_proxy


def test_lazy_proxy():
    graph = Graph()
    graph.register_instance("dict", {"a": 1, "b": 2})
    new_proxy = LazyProxy("dict", graph)

    assert sorted(new_proxy.keys()) == ["a", "b"]
    assert sorted(new_proxy.values()) == [1, 2]


def test_lazy_proxy_function():
    graph = Graph()
    graph.register_instance(Graph, graph)

    new_proxy = lazy_proxy("foo", graph=graph)

    assert isinstance(new_proxy, LazyProxy)


def test_module(graph):
    assert "tomate.proxy" in graph.providers
