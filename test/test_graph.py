from __future__ import unicode_literals

from wiring import Graph


def test_returns_graph_instance(graph):
    assert Graph in graph.providers
