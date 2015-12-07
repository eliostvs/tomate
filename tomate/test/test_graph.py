import unittest

from wiring import Graph

from tomate.graph import graph


class GraphTest(unittest.TestCase):

    def test_returns_graph_instance(self):
        self.assertIsInstance(graph.get(Graph), Graph)
