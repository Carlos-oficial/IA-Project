from typing import Dict, Set

import networkx as nx

from ia.place import Place
from ia.road import Road


class Map:
    """
    # Mapa
    Grafo não direcionado de locais.

    Os nodos estão guardados num dicionário nome:Place
    As arestas estão guardadas num set.

    Os nodos são objetos da classe Place, e as arestas são Roads
    """

    def __init__(self):
        self.places: Dict[str, Place] = {}
        self.roads: Set[Road] = set({})

    def add_road(self, place1: Place, place2: Place, length):
        self.roads.add(Road(place1, place2, length))
        self.places[place1.name] = place1
        self.places[place2.name] = place2

    def get_neighbours(self, place):
        return list(filter(lambda r: r.get_sorce() == place, self.roads))

    def get_place(self, name: str) -> Place:
        ret = self.places.get(name)
        if ret is None:
            raise Exception("Place not found")
        return ret

    def networkx_graph(self):
        """
        converte um mapa para um grafo da biblioteca networkx
        """
        G = nx.Graph()
        for node in self.places.keys():
            G.add_node(node)

        for edge in self.roads:
            G.add_edge(edge.src.name, edge.to.name, weight=edge.length)

        return G

    # end def
