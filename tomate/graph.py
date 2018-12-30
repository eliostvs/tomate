from wiring import Graph
from wiring.scanning import register

graph = Graph()
graph.register_instance(Graph, graph)

register.instance(Graph)(graph)
