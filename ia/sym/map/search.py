from ia.sym.map.map import Map
from typing import List, Dict, Set, Tuple
import heapq
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic


class SearchResult:
    def __init__(
        self,
        path: List[int],
        map: Map = None,
        search_tree: Dict[int, int] = dict(),
        explored=set(),
    ):
        self.map: Map = map
        self.path = path
        self.search_tree: Dict[int, int] = search_tree
        self.explored: Set[int] = explored

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
        route_edges = set(zip(self.path[1:], self.path)).union(
            set(zip(self.path, self.path[1:]))
        )
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
            node_color=nc,
            node_size=5,
            edge_color=edge_colors,
            bgcolor="k",
        )

        fig = ox.plot_graph_route(
            self.map.graph,
            self.path,
            ax=ax,
            route_linewidth=6,
            route_color=color,
            node_size=10,
            bgcolor="k",
        )

        plt.show()


class Search:
    def __init__(self, map: Map):
        self.map = map

    def run() -> SearchResult:
        pass


class ClassicalSearch(Search):
    def __init__(self, map: Map):
        super().__init__(map)
        self.explored: Set[int] = set()
        self.search_tree: Dict[int, int] = dict()
        self.current_node: int = None


class UninformedSearch(ClassicalSearch):
    def __init__(self, map, pop_index):
        super().__init__(map)
        self.pop_index: int = pop_index

    def run(self, src, dest):
        stack = [(src, [src])]  # Stack containing (current_node, path_so_far)
        self.explored = set()
        self.search_tree = dict()
        while stack:
            self.current_node, path = stack.pop(self.pop_index)

            if self.current_node == dest:
                return SearchResult(
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
        return SearchResult(
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

    def run(self, src, dest):
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
                return SearchResult(
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
        return SearchResult(
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
        super().__init__(map)
        self.meta_heuristic = meta_heuristic
        self.alg = alg

    def run(self, src, *nodes):
        missing = list(nodes)
        curr_node = src
        route = [src]
        while missing:
            missing.sort(
                key=lambda candidate: self.meta_heuristic(curr_node, candidate)
            )
            next = missing.pop(0)
            route += self.alg.run(curr_node, next).path[1:]
            curr_node = next

        route += self.alg.run(curr_node, src).path[1:]
        return SearchResult(route, map=self.map)
