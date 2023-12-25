import heapq
import string
from typing import Any, Dict, List, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic

from ia.sym.map.place import Place
from ia.sym.map.road import Road
from ia.ui.map_generator import MapGeneratorState


class Map:
    _id = 0

    def __init__(self, location: str, filepath: str):
        self.graph: nx.MultiDiGraph = None
        self.geo_features: gpd.GeoDataFrame = None
        self.location: str = location
        self.filepath: str = filepath

        self._reference_point: Tuple[float, float] = (0.0, 0.0)

        self.pickup_points: Dict[str, int] = dict()
        self.places: Dict[int, Place] = dict()
        self.roads: Set[Road] = set({})
        self.roads_mapped: dict = dict()
        # variaveis para cache
        self._node_positions: Dict[int, Tuple[float, float]] = dict()
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
        G = ox.graph_from_place(location, network_type="drive")
        return ox.get_undirected(G)

    def load_map_from_file(self) -> nx.MultiDiGraph:
        # Load the graph from the GraphML file
        self.graph = ox.load_graphml(self.filepath)
        return self.graph

    def fetch_map(self):
        try:
            self.load_map_from_file()
        except Exception as e:
            g = ox.graph_from_place(self.location, network_type="drive")
            G = ox.get_undirected(g)
            self.geo_features = ox.features_from_place(
                self.location, {"building": True, "highway": True}
            )
            self.from_nx_graph(G)
            # Save the graph to a GraphML file

            a = list(string.ascii_uppercase)
            i = 0
            for node, data in self.graph.nodes(data=True):
                data["name"] = Map.new_unique_name()
            ox.save_graphml(self.graph, filepath=self.filepath)
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

    def from_nx_graph(self, G):
        self.graph = G
        reference_lat = self.graph.nodes[list(self.graph.nodes())[0]]["y"]
        reference_lon = self.graph.nodes[list(self.graph.nodes())[0]]["x"]
        self._reference_point = (reference_lat, reference_lon)

        # Add nodes (places) to the map
        for node, data in G.nodes(data=True):
            self._node_data: Dict[node] = data

            self._node_positions[node] = self.referential_distance(data["y"], data["x"])
            name = data.get("name")
            if name is None:
                name = node
            self._node_names[node] = name
            self._name_nodes[name] = node
            warehouse = data.get("pickup")
            if warehouse is not None:
                self.pickup_points[warehouse] = node

            place = Place(name, x=data["x"], y=data["y"], id=node)
            self.places[node] = place

        for u, v, k in self.graph.edges(data=True):
            place1 = self.places[u]
            place2 = self.places[v]
            length = k["length"]
            self.add_road(place1, place2, length)

        return map

    def plot_map(self, show_edge_lables=False, route=None):
        fig, ax = ox.plot_graph(
            self.graph,
            node_size=0,
            edge_color="w",
            edge_alpha=0.6,
            bgcolor="k",
            show=False,
        )

        labels = self.node_names()
        node_color = ["b" for node in self.graph.nodes]

        nx.draw_networkx_labels(
            self.graph,
            self._node_positions,
            labels=labels,
            font_color="w",
            font_size=10,
            font_weight="light",
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,  # Specify the axis to draw on
        )

        nx.draw_networkx_nodes(
            self.graph,
            self._node_positions,
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
                self._node_positions,
                edge_labels=edge_labels,
                font_color="w",
                font_size=8,
                bbox=dict(facecolor="red", alpha=0.0),
                ax=ax,
            )

        # Plot all nodes in blue
        for node, (x, y) in self._node_positions.items():
            plt.scatter(x, y, color="blue", marker="o", s=30)
        plt.show()

    def plot_route(
        self, route: List[int], color="red", explored: set = {}, parents: dict = None
    ):
        nc = [
            "r" if node in route else "g" if node in explored else "w"
            for node in self.graph.nodes
        ]
        route_edges = set(zip(route[1:], route)).union(set(zip(route, route[1:])))
        tree_edges = Map.get_tree_edges(parents)

        edge_colors = []
        for x, y, _ in self.graph.edges:
            if (x, y) in route_edges or (y, x) in route_edges:
                edge_colors.append("red")
            elif (x, y) in tree_edges or (y, x) in tree_edges:
                edge_colors.append("green")
            else:
                edge_colors.append("w")

        fig, ax = ox.plot_graph(
            self.graph, node_color=nc, node_size=5, edge_color=edge_colors, bgcolor="k"
        )

        # nx.draw_networkx_edges(self.graph, pos=self._node_positions, edge_color=edge_colors, width=0.5)

        fig = ox.plot_graph_route(
            self.graph,
            route,
            ax=ax,
            route_linewidth=6,
            route_color=color,
            node_size=10,
            bgcolor="k",
        )

        plt.show()

    def add_road(self, place1: Place, place2: Place, length):
        road = Road(place1, place2, length)
        self.roads.add(road)
        if self.roads_mapped.get(place1.id) is None:
            self.roads_mapped[place1.id] = dict()

        if self.roads_mapped.get(place2.id) is None:
            self.roads_mapped[place2.id] = dict()
        self.roads_mapped[place1.id][place2.id] = road
        self.roads_mapped[place2.id][place1.id] = road

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
        return ox.distance.euclidean_dist_vec(uy, ux, vy, vx)

    def _edge_length(self, u, v) -> float:
        edge_data = self.graph.get_edge_data(u, v)
        return edge_data[0]["length"]

    def edge_length(self, u, v) -> float:
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
            edge_data = self.roads_mapped[u][v]
        return total_weight

    @staticmethod
    def get_tree_edges(parents):
        tree_edges = set()

        for child, parent in parents.items():
            if parent is not None:
                tree_edges.add((parent, child))

        return tree_edges

    def uninformed_search(self, src, dest, index=-1):
        stack = [(src, [src])]  # Stack containing (current_node, path_so_far)
        closed_set = set()
        parents = dict()

        while stack:
            current_node, path = stack.pop(index)

            if current_node == dest:
                return {"route": (path), "explored": closed_set, "parents": parents}

            if current_node in closed_set:
                continue

            closed_set.add(current_node)

            for neighbor_node in self.neighbours(current_node):
                if neighbor_node not in closed_set:
                    stack.append((neighbor_node, path + [neighbor_node]))
                    parents[neighbor_node] = current_node

        # If no path is found
        return {"route": (None), "explored": closed_set, "parents": parents}

    def best_first_search(self, src, dest, f, h):
        start = src
        end = dest
        open_set = [(0, start)]
        closed_set = set()
        parents = dict()
        costs = dict()

        heapq.heappush(open_set, (0, start))
        parents[start] = None
        costs[start] = 0
        checked = 0

        while open_set:
            checked += 1
            current_cost, current_node = heapq.heappop(open_set)

            if current_node == end:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = parents[current_node]
                return {
                    "route": list(reversed(path)),
                    "explored": closed_set,
                    "parents": parents,
                }

            if current_node in closed_set:
                continue

            closed_set.add(current_node)

            for neighbor_node in self.neighbours(current_node):
                new_cost = costs[current_node] + self.edge_length(
                    current_node, neighbor_node
                )
                estimated_cost = h(neighbor_node, dest)
                total_cost = f(new_cost, estimated_cost)

                if neighbor_node not in closed_set:
                    if neighbor_node not in costs or new_cost < costs[neighbor_node]:
                        costs[neighbor_node] = new_cost
                        heapq.heappush(open_set, (total_cost, neighbor_node))
                        parents[neighbor_node] = current_node

        raise Exception("No path found")

    def a_star_search(self, src, dest):
        def f(cost, heuristic):
            return cost + heuristic

        def h(n1, n2):
            print(self.distance(n1, n2))
            return self.distance(n1, n2)

        return self.best_first_search(src, dest, f, h)

    def greedy_search(self, src, dest):
        def f(cost, heuristic):
            return heuristic

        def h(n1, n2):
            print(self.distance(n1, n2))
            return self.distance(n1, n2)

        return self.best_first_search(src, dest, f, h)

    def uniform_cost_search(self, src, dest):
        def f(cost, heuristic):
            return cost

        def h(n1, n2):
            print(self.distance(n1, n2))
            return self.distance(n1, n2)

        return self.best_first_search(src, dest, f, h)

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
