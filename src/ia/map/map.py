import heapq
import random
import string
from typing import Any, Dict, List, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic

from ia.map.place import Place
from ia.map.road import Road
from ia.ui.map_generator import MapGeneratorState


class Problem:
    pass


class Map(Problem):
    _id = 0

    def __init__(self, location: str, filepath: str):
        self.graph: nx.MultiDiGraph = None
        self.geo_features: gpd.GeoDataFrame = None
        self.location: str = location
        self.filepath: str = filepath

        self._reference_point: Tuple[float, float] = (0.0, 0.0)

        self.factor = 1.6
        self.pickup_points: Dict[str, int] = dict()
        self.places: Dict[int, Place] = dict()
        self.roads: Set[Road] = set({})
        self.roads_mapped: dict = dict()

        # variaveis para cache
        self._node_positions: Dict[int, Tuple[float, float]] = dict()
        self._render_positions: dict = dict()
        self._node_data: Dict[int, Dict[str, Any]] = dict()
        self._node_names: Dict[int, str] = dict()
        self._name_nodes: Dict[str, int] = dict()
        self._neighbours: Dict[int, Set[int]] = dict()

    @staticmethod
    def new_unique_name():
        def number_to_letters(n):
            result = ""
            while n >= 0:
                result = chr(n % 26 + 65) + result
                n = n // 26 - 1
            return result

        i = Map._id
        Map._id += 1
        return number_to_letters(i)

    @staticmethod
    def download_graph(location):
        return ox.graph_from_place(location, network_type="drive")

    def load_map_from_file(self) -> nx.MultiDiGraph:
        return ox.load_graphml(self.filepath)

    def fetch_map(self):
        try:
            g = ox.load_graphml(self.filepath)
        except Exception as e:
            g = ox.graph_from_place(self.location, network_type="drive")
        G = ox.get_undirected(g)
        self.geo_features = ox.features_from_place(
            self.location, {"building": True, "highway": True}
        )

        self.from_nx_graph(G)
        ox.save_graphml(G, filepath=self.filepath)

        return self.graph

    @staticmethod
    def convert_to_meters(lat1, lon1, lat2, lon2):
        return geodesic((lat1, lon1), (lat2, lon2)).meters

    def referential_distance(self, lat, lon):
        """
        lat, lon = data['y'], data['x']
        """
        delta_lat = Map.convert_to_meters(
            self._reference_point[0],
            self._reference_point[1],
            lat,
            self._reference_point[1],
        )
        delta_lon = Map.convert_to_meters(
            self._reference_point[0],
            self._reference_point[1],
            self._reference_point[0],
            lon,
        )
        return (delta_lon, delta_lat)

    @staticmethod
    def from_map_gen_state(state: MapGeneratorState):
        map = Map(state.location, state.path)
        map.geo_features = state.gdf
        map.graph = state.G
        map.from_nx_graph(state.G)
        return map

    def from_nx_graph(self, G: nx.MultiDiGraph, name_nodes: bool = False):
        self.graph = G
        fst_node_data = self.graph.nodes[list(self.graph.nodes())[0]]
        reference_lat = fst_node_data["y"]
        reference_lon = fst_node_data["x"]
        self._reference_point = (reference_lat, reference_lon)
        name_nodes: bool = fst_node_data.get("name") is None
        if name_nodes:
            for node, data in self.graph.nodes(data=True):
                data["name"] = Map.new_unique_name()

        # Add nodes (places) to the map
        for node, data in self.graph.nodes(data=True):
            self._node_data: Dict[node] = data

            self._node_positions[node] = self.referential_distance(data["y"], data["x"])
            self._render_positions[node] = (data["x"], data["y"])
            name = data.get("name")
            if name is None:
                name = node
            self._node_names[node] = name
            self._name_nodes[name] = node
            warehouse = data.get("pickup")
            if warehouse is not None:
                self.pickup_points[warehouse] = node

            place = Place(
                name,
                x=self._node_positions[node][0],
                y=self._node_positions[node][1],
                id=node,
            )
            self.places[node] = place

        for u, v, k in self.graph.edges(data=True):
            place1 = self.places[u]
            place2 = self.places[v]
            length = k["length"]
            self.add_road(place1, place2, length)

        return map

    def plot(
        self,
        show_node_lables=True,
        show_edge_lables=False,
        route=None,
        show=True,
        highlight: Set[int] = {},
    ):
        fig, ax = ox.plot_graph(
            self.graph,
            node_size=0,
            edge_color="w",
            edge_alpha=0.6,
            bgcolor="k",
            show=False,
        )
        nx.draw_networkx_labels(
            self.graph,
            pos=self._render_positions,
            labels={node: name for name, node in self.pickup_points.items()},
            bbox=dict(facecolor="skyblue", alpha=0.5),
            font_color="b",
            font_size=10,
            font_weight="bold",
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )
        if show_node_lables:
            nx.draw_networkx_labels(
                self.graph,
                pos=self._render_positions,
                labels=self._node_names,
                font_color="w",
                font_size=10,
                font_weight="light",
                horizontalalignment="right",
                verticalalignment="bottom",
                ax=ax,
            )

        node_color = ["r" if node in highlight else "w" for node in self.graph.nodes]

        nx.draw_networkx_nodes(
            self.graph,
            self._render_positions,
            node_color=node_color,
            node_size=10,  # Adjust the size as needed
            ax=ax,
        )
        if show_edge_lables:
            edge_labels = {
                (u, v): f"{data['length']:.2f} m"
                for u, v, data in self.graph.edges(data=True)
            }
            nx.draw_networkx_edge_labels(
                self.graph,
                self._render_positions,
                edge_labels=edge_labels,
                font_color="w",
                font_size=8,
                bbox=dict(facecolor="red", alpha=0.0),
                ax=ax,
            )

        if show:
            plt.show()
        return fig, ax

    def add_road(self, place1: Place, place2: Place, length):
        road = Road(place1, place2, length)
        road2 = Road(place2, place1, length)
        self.roads.add(road)
        self.roads.add(road2)
        if self.roads_mapped.get(place1.id) is None:
            self.roads_mapped[place1.id] = dict()

        if self.roads_mapped.get(place2.id) is None:
            self.roads_mapped[place2.id] = dict()
        self.roads_mapped[place1.id][place2.id] = road
        self.roads_mapped[place2.id][place1.id] = road2

    def get_node_by_name(self, name):
        if self._name_nodes.get(name) is not None:
            return self._name_nodes[name]
        for node, n in self._node_names.items():
            self._name_nodes[n] = n
            if name == n:
                return node

        raise ValueError("name doesnt exist")

    def distance(self, u: int, v: int) -> float:
        ux, uy = self._node_positions[u]
        vx, vy = self._node_positions[v]
        return ((uy - vy) ** 2 + (ux - vx) ** 2) ** 0.5

    def _edge_length(self, u, v) -> float:
        edge_data = self.graph.get_edge_data(u, v)
        return edge_data[0]["length"]

    def cost_function(self, u, v):
        return self.road_length(u, v)

    def road_length(self, u, v) -> float:
        try:
            road: Road = self.roads_mapped[u][v]
            return road.length
        except Exception as e:
            return 10000000  # infinito

    def get_place(self, name: str) -> Place:
        ret = self.places.get(name)
        if ret is None:
            raise Exception("Place not found")
        return ret

    def get_road(self, src: str, dest: str) -> Road:
        try:
            road: Road = self.roads_mapped[src][dest]
            return road
        except Exception as e:
            raise ValueError("Road was not found")

    def central_node(self) -> int:
        # Calculate closeness centrality
        closeness_centrality = nx.closeness_centrality(self.graph)

        # Find the node with the highest closeness centrality
        return max(closeness_centrality, key=closeness_centrality.get)

    def neighbours(self, node):
        cached = self._neighbours.get(node)
        if cached is not None:
            return cached
        self._neighbours[node] = set(self.graph.neighbors(node))
        return self._neighbours[node]

    def path_length(self, path: List[int]) -> float:
        total_weight = 0.0

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            total_weight += self._edge_length(u, v)
        return total_weight

    def test_distances(self):
        for edge in self.graph.edges(data=True):
            u, v, data = edge
            length = data["length"]
            distance = self.distance(u, v)
            euclidean_distance = Map.convert_to_meters(
                self.graph.nodes[u]["y"],
                self.graph.nodes[u]["x"],
                self.graph.nodes[v]["y"],
                self.graph.nodes[v]["x"],
            )

            print(
                f"Edge: ({u}, {v}), Length: {length} meters, Euclidean Distance: {euclidean_distance} meters, self.Distance:{distance}"
            )
