import json
from ctypes import Union
from typing import Dict, List, Set

import networkx as nx

from ia.map.place import Place
from ia.map.road import Road


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

    def get_neighbours(self, place):
        return list(filter(lambda r: r.get_source() == place, self.roads))

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

    def path_length(self, path: List[str]) -> float:
        ret: float = 0.0
        for pair in zip(path, path[1:]):
            road = self.get_road(*pair)
            ret += road.length
        return ret

    # Converte um json para Map
    @staticmethod
    def load(file_path: str) -> "Map":
        with open(file_path, "r") as file:
            map_data = json.load(file)

        places_data: List[Dict[str, str]] = map_data.get("places", [])
        roads_data: List[Dict[str, Union[str, int]]] = map_data.get("roads", [])

        my_map = Map()

        # Add places to the map
        for place_info in places_data:
            place_name = place_info.get("name")
            place = Place(name=place_name)
            my_map.places[place_name] = place

        # Add roads to the map
        for road_info in roads_data:
            place1 = my_map.get_place(road_info["place1"])
            place2 = my_map.get_place(road_info["place2"])
            length = road_info["length"]
            my_map.add_road(place1, place2, length)

        return my_map

    # NETWORKX
    #
    #
    #

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

    def calculate_path(self, src: str, dest: str) -> List[str]:
        print(src)
        print(self.places.keys())
        if src not in self.places.keys() or dest not in self.places.keys():
            raise Exception("source and/or destination not found")

        def weight_function(a, b, x) -> float:
            length_factor = (
                x["road"].length / x["road"].vel_cap()
                if x["road"].vel_cap() != 0
                else 10000000
            )

            return length_factor

        return nx.shortest_path(
            self.networkx_graph(),
            source=src,
            target=dest,
            weight=weight_function,
        )

    # end def
