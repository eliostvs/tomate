from __future__ import unicode_literals

from wiring import Graph

graph = Graph()
graph.register_instance(Graph, graph)