import heapq
import random
from typing import Dict, List, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic

from ia.map.map import Map


class SearchResult:
    pass


class SearchResultOnMap(SearchResult):
    def __init__(
        self,
        path: List[int],
        map: Map = None,
        search_tree: Dict[int, int] = dict(),
        explored=set(),
        nodes_to_highlight=set(),
        **kwargs,
    ):
        self.map: Map = map
        self.path = path
        self.search_tree: Dict[int, int] = search_tree
        self.explored: Set[int] = explored
        self.nodes_to_highlight = nodes_to_highlight
        self.pseudo_route = kwargs.get("pseudo_route")
        self.passed_kwargs = kwargs

    def __repr__(self):
        return f"SearchResult(path={self.path}\n search_tree={self.search_tree}\n explored={self.explored},kwargs={self.passed_kwargs})"

    def condense(self, path_cost):
        return {
            "path_n": len(self.path),
            "path_cost": path_cost(self.path),
            "explored_n": len(self.explored),
        }

    def get_tree_edges(self) -> Set[Tuple[int, int]]:
        tree_edges = set()

        for child, parent in self.search_tree.items():
            if parent is not None:
                tree_edges.add((parent, child))

        return tree_edges

    def plot(self, color="red", show=True):
        nc = [
            "#FFFF00"
            if type(self.pseudo_route)==list and node in self.pseudo_route
            else "r"
            if node in self.path
            else "g"
            if node in self.explored
            else "w"
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
            node_size=10,
            node_color=nc,
            edge_color=edge_colors,
            edge_alpha=0.6,
            bgcolor="k",
            show=False,
        )

        nx.draw_networkx_labels(
            self.map.graph,
            pos=self.map._render_positions,
            labels={
                node: name
                for node, name in self.map._node_names.items()
                if node in self.path
            },
            font_color="w",
            font_size=10,
            font_weight="light",
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )

        # for node, (x, y) in [
        #     (node, (x, y))
        #     for (node, (x, y)) in self.map._render_positions.items()
        #     if node in self.nodes_to_highlight
        # ]:
        #     plt.scatter(x, y, color="blue", marker="o", s=30)

        start = self.path[0]
        end = self.path[-1]
        ax.set_title(
            f"searched from {self.map._node_names[start]} to {self.map._node_names[end]}"
        )
        if show:
            plt.show()
        return fig, ax


class Search:
    def run(self, src,dest,reset=False) -> SearchResult:
        pass

    def __str__(self):
        return self.__class__.__name__


class ClassicalSearch(Search):
    def __init__(self, map: Map, cost_function=None):
        if cost_function is None:
            if hasattr(map, "cost_function"):
                self.cost_function = map.cost_function
            self.cost_function = map.road_length
        else:
            self.cost_function = cost_function
        self.map = map
        self.explored: Set[int] = set()
        self.search_tree: Dict[int, int] = dict()
        self.current_node: int = None

    def reset(self):
        self.explored: Set[int] = set()
        self.search_tree: Dict[int, int] = dict()
        self.current_node: int = None


class UninformedSearch(ClassicalSearch):
    OPTIMAL = True

    def __init__(self, map, pop_index, cost_function=None):
        super().__init__(map, cost_function=cost_function)
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
    OPTIMAL = False

    def __init__(self, map):
        super().__init__(map, -1)


class BFS(UninformedSearch):
    OPTIMAL = False

    def __init__(self, map):
        super().__init__(map, 0)


class BestFirstSearch(ClassicalSearch):
    def __init__(self, map, h, f, cost_function=None):
        super().__init__(map, cost_function)
        self.heuristic = h
        self.optimization_function = f
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
                new_cost = self.costs[current_node] + self.cost_function(
                    current_node, neighbor_node
                )
                estimated_cost = self.heuristic(neighbor_node, dest)
                total_cost = self.optimization_function(new_cost, estimated_cost)

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
    OPTIMAL = True

    def __init__(self, map, h, cost_function=None):
        def f(cost, heuristic):
            return cost + heuristic

        super().__init__(map, h, f, cost_function=cost_function)


class GreedySearch(BestFirstSearch):
    OPTIMAL = False

    def __init__(self, map, h, cost_function=None):
        def f(cost, heuristic):
            return heuristic

        super().__init__(map, h, f, cost_function=cost_function)


class UniformCostSearch(BestFirstSearch):
    OPTIMAL = True

    def __init__(self, map, cost_function=None):
        def f(cost, heuristic):
            return cost

        super().__init__(map, lambda x, y: 0, f, cost_function=cost_function)


class TourSearch(Search):
    OPTIMAL = False

    def __init__(self, map, meta_heuristic, alg: ClassicalSearch, cost_function=None):
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


class RestrictedTourSearch(Search):
    def __init__(self, map, meta_heuristic, alg: ClassicalSearch):
        self.map = map
        self.meta_heuristic = meta_heuristic
        self.alg = alg
        self.nodes_in_tour = list()
        self.pseudo_route = []

    def run(self, src, nodes: Set[int], order_restrictions: Dict[int, Set[int]]):
        self.nodes_in_tour = [src] + list(nodes)
        missing = set(nodes)
        completed = set()
        curr_node = src
        route = [src]
        self.pseudo_route = [src]
        while missing:
            possible = missing.intersection(
                {n for n in nodes if not order_restrictions.get(n)}
            )
            next = min(
                possible,
                key=lambda candidate: self.meta_heuristic(curr_node, candidate),
            )
            missing.remove(next)
            self.pseudo_route.append(next)

            for g, s in order_restrictions.items():
                try:
                    s.remove(next)
                except Exception as e:
                    pass

            r = self.alg.run(curr_node, next)
            self.alg.reset()
            route += r.path[1:]
            curr_node = next
        return SearchResultOnMap(
            route,
            pseudo_route=self.pseudo_route,
            map=self.map,
            nodes_to_highlight={node for node in self.nodes_in_tour},
        )


class AndOrRestrictedTourSearch(Search):
    OPTIMAL = False

    def __init__(self, map, meta_heuristic, alg: ClassicalSearch):
        self.map = map
        self.meta_heuristic = meta_heuristic
        self.alg = alg
        self.nodes_in_tour = list()
        self.pseudo_route = []

    def run(
        self, src, nodes: Set[int], order_restrictions: Dict[int, Set[int | Tuple[int]]]
    ):
        """
        A:{X,[Z,Y]} A depende de X e de (Z ou Y)
        """
        self.nodes_in_tour = [src] + list(nodes)
        restrictions = {**{n: set() for n in nodes}, **order_restrictions}
        missing = nodes
        completed = set()
        curr_node = src
        route = [src]
        self.pseudo_route = [src]

        def done():
            return restrictions and nodes.intersection(set(restrictions.keys()))

        while done():
            print("completed=", completed)
            print("curr_node=", curr_node)
            print("route=", route)
            print("restrictions=", restrictions)

            possible = set()
            for k, v in restrictions.items():
                possible.add(k)
                for r in v:
                    if type(r) == tuple:
                        possible = possible.union(set(r))
                    if type(r) == int:
                        possible.add(r)

            print("possible=", possible)
            candidates = {node for node in possible if not restrictions.get(node)}

            def min_func(curr_node, candidate):
                if type(candidate) == int:
                    return self.meta_heuristic(curr_node, candidate)
                if type(candidate) == tuple:
                    return min(list(candidate), key=lambda x: min_func(curr_node, x))

            print("candidates = ", candidates)

            next = min(candidates, key=lambda x: min_func(curr_node, x))
            print("next = ", next)

            for depends, restriction in restrictions.items():
                if next in restriction:
                    restriction.remove(next)
                to_pop = []
                for item in restriction:
                    if type(item) == tuple and next in item:
                        to_pop.append(item)

                for item in to_pop:
                    restriction.remove(item)
            try:
                restrictions.pop(next)
            except:
                pass
            print("restrictions=", restrictions)
            self.pseudo_route.append(next)

            r = self.alg.run(curr_node, next)
            self.alg.reset()
            route += r.path[1:]
            curr_node = next
        return SearchResultOnMap(
            route,
            pseudo_route=self.pseudo_route,
            map=self.map,
            nodes_to_highlight={node for node in self.nodes_in_tour},
        )


class DeliverySearch(Search):
    OPTIMAL = False

    def __init__(self, map, meta_heuristic, alg: ClassicalSearch):
        self.map = map
        self.meta_heuristic = meta_heuristic
        self.alg = alg
        self.nodes_in_tour = list()
        self.pseudo_route = []

    def run(
        self, src, dest , order_restrictions: Set[int | Tuple[int]]
    ):
        """
        A:{X,[Z,Y]} A depende de X e de (Z ou Y)
        """
        self.nodes_in_tour = [src]
        self.curr_path = self.alg.run(src,dest,reset=True)
        restrictions = {dest:order_restrictions}
        completed = set()
        curr_node = src
        route = [src]
        self.pseudo_route = [src,dest]

        def not_done():
            return restrictions # and nodes.intersection(set(restrictions.keys()))

        intial_path = self.alg.run(src,dest)
        while not_done():
            print("curr_node",curr_node)            
            print("restrictions=", restrictions)
            for depends, restriction in restrictions.items():
                if curr_node in restriction:
                    restriction.remove(curr_node)
                to_pop = []
                for item in restriction:
                    if type(item) == tuple and curr_node in item:
                        to_pop.append(item)

                for item in to_pop:
                    restriction.remove(item)
            try:
                restrictions.pop(curr_node)
            except:
                pass
            if not restrictions: break

            possible = set()
            for k, v in restrictions.items():
                possible.add(k)
                for r in v:
                    if type(r) == tuple:
                        possible = possible.union(set(r))
                    if type(r) == int:
                        possible.add(r)

            
            candidates = {node for node in possible if not restrictions.get(node)}

            def min_func(curr_node, candidate):
                if type(candidate) == int:
                    cost = 1000000 # aka +inf
                    for index,node in enumerate( self.pseudo_route):
                        if self.meta_heuristic(node,candidate)<cost:
                            cost = self.meta_heuristic(node,candidate)
                    return cost
                
                if type(candidate) == tuple:
                    return min(list(candidate), key=lambda x: min_func(curr_node, x))


            next = min(candidates, key=lambda x: min_func(curr_node, x))

            
            edges  = list(zip(self.pseudo_route[:-1],self.pseudo_route[1:]))
            
            edge_to_expand = min(edges, key=lambda pair:self.meta_heuristic(pair[0],next)+self.meta_heuristic(next,pair[1]))
                
            index = edges.index(edge_to_expand)+1
            self.pseudo_route.insert(index,next)
            curr_node = next
            print("\n\n")

        result = [self.pseudo_route[0]]  # Initialize the result with the first element

        for elem in self.pseudo_route[1:]:
            if elem != result[-1]:
                result.append(elem)

        self.pseudo_route = result
        for curr_node,next in zip(self.pseudo_route[:-1],self.pseudo_route[1:]):
            r = self.alg.run(curr_node, next,reset=True)
            print(r.path)
            
            route += r.path[1:]
        return SearchResultOnMap(
            route,
            pseudo_route=self.pseudo_route,
            map=self.map,
            nodes_to_highlight={node for node in self.nodes_in_tour},
        )
