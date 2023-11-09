from typing import Dict, Set, List

import networkx as nx

from ia.place import Place
from ia.road import Road
from ia.veichle import Veichle


class Map:
    """
    # Mapa
    Grafo não direcionado de locais.

    Os nodos estão guardados num dicionário nome:Place
    As arestas estão guardadas num set.

    Os nodos são objetos da classe Place, e as arestas são Roads
    """

    def __init__(self) -> None:
        self.places: Dict[str, Place] = dict({})
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

    def get_road(self, src: str, dest: str) -> Road:
        for road in self.roads:
            if road.src.name == src and road.to.name == dest:
                return road
        raise Exception("Road not found")

    def networkx_graph(self):
        """
        converte um mapa para um grafo da biblioteca networkx
        """
        G = nx.Graph()
        for node in self.places.keys():
            G.add_node(node)

        for road in self.roads:
            G.add_edge(
                road.src.name, road.to.name, road=road
            )  # temos a informação sobre as estradas, e esta é mutável
        return G

    def calculate_path(self, src: str, dest: str):
        print(src)
        print(self.places.keys())
        if src not in self.places.keys() or dest not in self.places.keys():
            raise Exception("source and/or destination not found")
        return nx.shortest_path(
            self.networkx_graph(),
            source=src,
            target=dest,
            weight=lambda a, b, x: x["road"].length / x["road"].vel_cap()
            if x["road"].vel_cap() != 0
            else 10000000,
        )

    def path_length(self, path: List[str]) -> float:
        ret: float = 0.0
        for pair in zip(path, path[1:]):
            road = self.get_road(*pair)
            ret += road.length
        return ret

    # end def
