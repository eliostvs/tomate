import unittest

from wiring import Graph

from tomate.graph import graph


class TestGraph(unittest.TestCase):
    def test_returns_graph_instance(self):
        self.assertIsInstance(graph.get(Graph), Graph)