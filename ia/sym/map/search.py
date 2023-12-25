from ia.sym.map.map import Map
from typing import List, Dict, Set, Tuple
import heapq
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic


class SearchResultOnMap:
    def __init__(
        self,
        path: List[int],
        map: Map = None,
        search_tree: Dict[int, int] = dict(),
        explored=set(),
        nodes_to_highlight=set(),
    ):
        self.map: Map = map
        self.path = path
        self.search_tree: Dict[int, int] = search_tree
        self.explored: Set[int] = explored
        self.nodes_to_highlight = nodes_to_highlight

    def __repr__(self):
        return f"SearchResult(path={self.path}\n search_tree={self.search_tree}\n explored={self.explored})"

    def get_tree_edges(self) -> Set[Tuple[int, int]]:
        tree_edges = set()

        for child, parent in self.search_tree.items():
            if parent is not None:
                tree_edges.add((parent, child))

        return tree_edges

    def plot(self, color="red"):
        nc = [
            "r" if node in self.path else "g" if node in self.explored else "w"
            for node in self.map.graph.nodes
        ]
        route_edges = set(zip(self.path[1:], self.path))
        tree_edges = self.get_tree_edges()

        edge_colors = []
        for x, y, _ in self.map.graph.edges:
            if (x, y) in route_edges or (y, x) in route_edges:
                edge_colors.append("red")
            elif (x, y) in tree_edges or (y, x) in tree_edges:
                edge_colors.append("green")
            else:
                edge_colors.append("w")

        fig, ax = ox.plot_graph(
            self.map.graph,
            node_size=0,
            node_color=nc,
            edge_color=edge_colors,
            edge_alpha=0.6,
            bgcolor="k",
            show=False,
        )

        nx.draw_networkx_labels(
            self.map.graph,
            pos=self.map._render_positions,
            labels=self.map._node_names,
            font_color="w",
            font_size=10,
            font_weight="light",
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )

        for node, (x, y) in [
            (node, (x, y))
            for (node, (x, y)) in self.map._render_positions.items()
            if node in self.nodes_to_highlight
        ]:
            plt.scatter(x, y, color="blue", marker="o", s=30)

        start = self.path[0]
        end = self.path[-1]
        ax.set_title(
            f"searched from {self.map._node_names[start]} to {self.map._node_names[end]}"
        )

        plt.show()


class Search:
    def run() -> SearchResultOnMap:
        pass


class ClassicalSearch(Search):
    def __init__(self, map: Map):
        self.map = map
        self.explored: Set[int] = set()
        self.search_tree: Dict[int, int] = dict()
        self.current_node: int = None

    def reset(self):
        self.explored: Set[int] = set()
        self.search_tree: Dict[int, int] = dict()
        self.current_node: int = None


class UninformedSearch(ClassicalSearch):
    def __init__(self, map, pop_index):
        super().__init__(map)
        self.pop_index: int = pop_index

    def run(self, src, dest, reset=False):
        if reset:
            self.reset()
        stack = [(src, [src])]  # Stack containing (current_node, path_so_far)
        self.explored = set()
        self.search_tree = dict()
        while stack:
            self.current_node, path = stack.pop(self.pop_index)

            if self.current_node == dest:
                return SearchResultOnMap(
                    map=self.map,
                    path=path,
                    search_tree=self.search_tree,
                    explored=self.explored,
                )

            if self.current_node in self.explored:
                continue

            self.explored.add(self.current_node)

            for neighbor_node in self.map.neighbours(self.current_node):
                if neighbor_node not in self.explored:
                    stack.append((neighbor_node, path + [neighbor_node]))
                    self.search_tree[neighbor_node] = self.current_node

        # If no path is found
        return SearchResultOnMap(
            map=self.map,
            path=None,
            search_tree=self.search_tree,
            explored=self.explored,
        )


class DFS(UninformedSearch):
    def __init__(self, map):
        super().__init__(map, -1)


class BFS(UninformedSearch):
    def __init__(self, map):
        super().__init__(map, 0)


class BestFirstSearch(ClassicalSearch):
    def __init__(self, map, h, f):
        super().__init__(map)
        self.h = h
        self.f = f
        self.costs = dict()

    def reset(self):
        super().reset()
        self.costs = dict()

    def run(self, src, dest, reset=False):
        if reset:
            self.reset()

        open_set = [(0, src)]

        heapq.heappush(open_set, (0, src))
        self.search_tree[src] = None
        self.costs[src] = 0

        while open_set:
            current_cost, current_node = heapq.heappop(open_set)

            if current_node == dest:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = self.search_tree[current_node]
                return SearchResultOnMap(
                    list(reversed(path)),
                    map=self.map,
                    explored=self.explored,
                    search_tree=self.search_tree,
                )
            if current_node in self.explored:
                continue

            self.explored.add(current_node)

            for neighbor_node in self.map.neighbours(current_node):
                new_cost = self.costs[current_node] + self.map.edge_length(
                    current_node, neighbor_node
                )
                estimated_cost = self.h(neighbor_node, dest)
                total_cost = self.f(new_cost, estimated_cost)

                if neighbor_node not in self.explored:
                    if (
                        neighbor_node not in self.costs
                        or new_cost < self.costs[neighbor_node]
                    ):
                        self.costs[neighbor_node] = new_cost
                        heapq.heappush(open_set, (total_cost, neighbor_node))
                        self.search_tree[neighbor_node] = current_node
        return SearchResultOnMap(
            map=self.map,
            path=[],
            search_tree=self.search_tree,
            explored=self.explored,
        )


class AStar(BestFirstSearch):
    def __init__(self, map, h):
        def f(cost, heuristic):
            return cost + heuristic

        super().__init__(map, h, f)


class GreedySearch(BestFirstSearch):
    def __init__(self, map, h):
        def f(cost, heuristic):
            return heuristic

        super().__init__(map, h, f)


class UniformedCostSearch(BestFirstSearch):
    def __init__(self, map, h):
        def f(cost, heuristic):
            return cost

        super().__init__(map, h, f)


class TourSearch(Search):
    def __init__(self, map, meta_heuristic, alg: ClassicalSearch):
        self.map = map
        self.meta_heuristic = meta_heuristic
        self.alg = alg
        self.nodes_in_tour = list()

    def run(self, src, *nodes):
        self.nodes_in_tour = [src] + list(nodes)
        missing = list(nodes)
        curr_node = src
        route = [src]
        while missing:
            missing.sort(
                key=lambda candidate: self.meta_heuristic(curr_node, candidate)
            )
            next = missing.pop(0)
            r = self.alg.run(curr_node, next)
            self.alg.reset()
            route += r.path[1:]
            curr_node = next

        r = self.alg.run(curr_node, src)

        route += r.path[1:]
        return SearchResultOnMap(
            route,
            map=self.map,
            nodes_to_highlight={node for node in self.nodes_in_tour},
        )
