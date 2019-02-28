from wiring import Graph
from wiring.scanning import scan_to_graph


def test_returns_graph_instance(graph):
    scan_to_graph(["tomate.graph"], graph)

    assert Graph in graph.providers
