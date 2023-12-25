import string
from typing import List, Dict, Tuple, Any, Set
import heapq

import networkx as nx
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt


class Map:
    def __init__(self, location: str, filepath: str):
        self.graph: nx.MultiDiGraph = None
        self.location: str = location
        self.filepath: str = filepath
        # variaveis para cache
        self._node_positions: Dict[int, Tuple[float, float]] = dict()
        self._node_data: Dict[int, Dict[str, Any]] = dict()
        self._node_names: Dict[int, str] = dict()
        self._names_nodes: Dict[str, int] = dict()
        self._neighbours: Dict[int, Set[int]] = dict()
        # vai buscar o mapa
        self.fetch_map()
        self.node_data()
        self.node_names()
        self.node_positions()

    def download_map(self):
        G = ox.graph_from_place(self.location, network_type="drive")
        self.graph = ox.get_undirected(G)
        # Save the graph to a GraphML file

        a = list(string.ascii_uppercase)
        i = 0

        for node, data in self.graph.nodes(data=True):
            data["name"] = a[i % len(a)] + str(int(i / len(a)))
            i += 1

        ox.save_graphml(self.graph, filepath=self.filepath)
        return self.graph

    def load_map_from_file(self) -> nx.MultiDiGraph:
        # Load the graph from the GraphML file
        self.graph = ox.load_graphml(self.filepath)
        return self.graph

    def plot_map(self, show_edge_lables=False, route=None):
        fig, ax = ox.plot_graph(
            self.graph,
            node_size=0,
            edge_color="w",
            edge_alpha=0.6,
            bgcolor="k",
            show=False,
        )

        self._node_positions = {
            node: (data["x"], data["y"]) for node, data in self.graph.nodes(data=True)
        }

        central_node = self.central_node()
        labels = {
            node: (data["name"] if node is not central_node else "")
            for node, data in self.graph.nodes(data=True)
        }
        node_color = ["r" if node == central_node else "b" for node in self.graph.nodes]

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

        # Plot the most central node in red and make it bigger
        x_central, y_central = self._node_positions[self.central_node()]
        plt.scatter(
            x_central,
            y_central,
            color="red",
            marker="o",
            s=100,
            label="Most Central Node",
        )

        plt.show()

    def plot_route(
        self, route: List[int], color="red", explored: set = {}, parents: dict = None
    ):
        nc = [
            "r" if node in route else "g" if node in explored else "w"
            for node in self.graph.nodes
        ]
        # for (u, v, k, c) in self.graph.edges(data='color', keys=True, default="red"):
        route_edges = set(zip(route[1:], route)).union(set(zip(route, route[1:])))
        print(route_edges)
        # edge_colors = ["r" if edge in route_edges else "b" for edge in self.graph.edges]

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

    def show_plot(self):
        plt.show()

    def central_node(self):
        degree_centrality = nx.degree_centrality(self.graph)
        most_central_node = max(degree_centrality, key=degree_centrality.get)
        return most_central_node

    def node_names(self):
        self._node_names = {
            node: (data["name"] if node is not self.central_node() else "")
            for node, data in self.graph.nodes(data=True)
        }
        return self._node_names

    def node_positions(self):
        self._node_positions = {
            node: (data["x"], data["y"]) for node, data in self.graph.nodes(data=True)
        }
        return self._node_positions

    def node_data(self):
        self._node_data = {node: data for node, data in self.graph.nodes(data=True)}
        return self._node_data

    def get_node_by_name(self, name):
        if self._names_nodes.get(name) is not None:
            return self._names_nodes[name]
        for node, n in self._node_names.items():
            self._names_nodes[n] = n
            if name == n:
                return node

        raise ValueError("name doesnt exist")

    def path_weight(self, path: List[int]) -> float:
        """
        Calcula o peso total de um caminho no grafo fornecido usando atributos de aresta.

        Parâmetros:
        - mapa: O grafo (rede) no qual o caminho está definido.
        - caminho (list): Uma lista de IDs de nós representando o caminho.

        Retorna:
        - float: O peso total do caminho.
        """
        total_weight = 0.0

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = self.graph.get_edge_data(u, v)[0]
            if edge_data is not None and "length" in edge_data:
                total_weight += edge_data["length"]
            else:
                raise Exception("Could not find edge")
        return total_weight

    def distance(self, u: int, v: int) -> float:
        ux, uy = self._node_positions[u]
        vx, vy = self._node_positions[v]
        return ox.distance.euclidean_dist_vec(uy, ux, vy, vx)

    def edge_length(self, u, v) -> float:
        edge_data = self.graph.get_edge_data(u, v)
        return edge_data[0]["length"]

    def neighbours(self, node):
        cached = self._neighbours.get(node)
        if cached is not None:
            return cached
        self._neighbours[node] = set(self.graph.neighbors(node))
        return self._neighbours[node]

    @staticmethod
    def get_tree_edges(parents):
        tree_edges = set()

        for child, parent in parents.items():
            if parent is not None:
                tree_edges.add((parent, child))

        return tree_edges

    def fetch_map(self):
        try:
            self.load_map_from_file()
        except Exception as e:
            self.download_map()
        return self.graph

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
            # print(f"Processing node: {current_node} {self._node_names[current_node]}")

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
        def f(weight, heuristic):
            return weight + heuristic

        def h(n1, n2):
            return self.distance(n1, n2)

        return self.best_first_search(src, dest, f, h)

    def greedy_search(self, src, dest):
        def f(weight, heuristic):
            return heuristic

        def h(n1, n2):
            return self.distance(n1, n2)

        return self.best_first_search(src, dest, f, h)

    def uniform_cost_search(self, src, dest):
        def f(cost, heuristic):
            return cost

        def h(n1, n2):
            return self.distance(n1, n2)

        return self.best_first_search(src, dest, f, h)


if __name__ == "__main__":
    map = Map("Gualtar, PT", "file")
    s = map.get_node_by_name("A0")
    d = map.get_node_by_name("G9")
    alg = input("algoritmo: ")
    if alg == "greedy":
        res = map.greedy_search(
            s,
            d,
        )
    elif alg == "A*":
        res = map.a_star_search(s, d)
    elif alg == "custo uniforme":
        res = map.uniform_cost_search(s, d)
    elif alg == "DFS":
        res = map.uninformed_search(s, d, index=-1)
    elif alg == "BFS":
        res = map.uninformed_search(s, d, index=0)

    map.plot_route(res["route"], explored=res["explored"], parents=res["parents"])
    map.show_plot()

    print(res["route"], len(res["explored"]))
