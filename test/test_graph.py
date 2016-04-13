from __future__ import unicode_literals

from wiring import Graph

from tomate.graph import graph


def test_returns_graph_instance():
    assert graph is graph.get(Graph)
