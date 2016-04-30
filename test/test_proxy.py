from __future__ import unicode_literals

from wiring import FunctionProvider, Graph

from tomate.proxy import LazyProxy, lazy_proxy, ProxyModule


def test_lazy_proxy():
    graph = Graph()
    graph.register_instance('dict', {'a': 1, 'b': 2})
    new_proxy = LazyProxy(graph, 'dict')

    assert new_proxy.keys() == ['a', 'b']
    assert new_proxy.values() == [1, 2]


def test_lazy_proxy_function():
    graph = Graph()
    graph.register_instance(Graph, graph)

    new_proxy = lazy_proxy('foo', graph=graph)

    assert isinstance(new_proxy, LazyProxy)


def test_proxy_module():
    graph = Graph()

    assert list(ProxyModule.providers.keys()) == ['tomate.proxy']

    ProxyModule().add_to(graph)

    provider = graph.providers['tomate.proxy']

    assert isinstance(provider, FunctionProvider)
    assert provider.scope is None

    assert provider.dependencies == {'graph': Graph}

    graph.register_instance(Graph, graph)

    func = graph.get('tomate.proxy')
    new_proxy = func(Graph)

    assert isinstance(new_proxy, LazyProxy)
