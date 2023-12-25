from ia.sym.map.map import Map
from typing import List, Dict, Set, Tuple


class SearchResult:
    def __init__(self, path: List[int], search_tree: Dict[int, int]):
        self.path = path
        self.search_tree: Dict[int, int] = search_tree
        self.explored: Set[int] = set()

    def __repr__(self):
        return f"SearchResult(path={self.path}\n search_tree={self.search_tree}\n explored={self.explored})"

    def get_tree_edges(self) -> Set[Tuple[int, int]]:
        tree_edges = set()

        for child, parent in self.search_tree.items():
            if parent is not None:
                tree_edges.add((parent, child))

        return tree_edges


class Search:
    def __init__(self, map: Map):
        self.map: Map = map
        self.explored: Set[int] = set()
        self.search_tree: Dict[int, int] = dict()
        self.current_node: int = None

    def run() -> SearchResult:
        pass


class UninformedSearch(Search):
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
                return SearchResult(path=path, search_tree=self.search_tree)

            if self.current_node in self.explored:
                continue

            self.explored.add(self.current_node)

            for neighbor_node in self.map.neighbours(self.current_node):
                if neighbor_node not in self.explored:
                    stack.append((neighbor_node, path + [neighbor_node]))
                    self.search_tree[neighbor_node] = self.current_node

        # If no path is found
        return SearchResult(path=None, search_tree=self.search_tree)


class DFS(UninformedSearch):
    def __init__(self, map):
        super().__init__(map, -1)


class BFS(UninformedSearch):
    def __init__(self, map):
        super().__init__(map, 0)


# def uninformed_search( src, dest, index=-1):
#     stack = [(src, [src])]  # Stack containing (current_node, path_so_far)
#     closed_set = set()
#     parents = dict()

#     while stack:
#         current_node, path = stack.pop(index)

#         if current_node == dest:
#             return {"route": (path), "explored": closed_set, "parents": parents}

#         if current_node in closed_set:
#             continue

#         closed_set.add(current_node)

#         for neighbor_node in self.neighbours(current_node):
#             if neighbor_node not in closed_set:
#                 stack.append((neighbor_node, path + [neighbor_node]))
#                 parents[neighbor_node] = current_node

#     # If no path is found
#     return {"route": (None), "explored": closed_set, "parents": parents}

# def best_first_search(self, src, dest, f, h):
#     start = src
#     end = dest
#     open_set = [(0, start)]
#     closed_set = set()
#     parents = dict()
#     costs = dict()

#     heapq.heappush(open_set, (0, start))
#     parents[start] = None
#     costs[start] = 0
#     checked = 0

#     while open_set:
#         checked += 1
#         current_cost, current_node = heapq.heappop(open_set)

#         if current_node == end:
#             path = []
#             while current_node is not None:
#                 path.append(current_node)
#                 current_node = parents[current_node]
#             return {
#                 "route": list(reversed(path)),
#                 "explored": closed_set,
#                 "parents": parents,
#             }

#         if current_node in closed_set:
#             continue

#         closed_set.add(current_node)

#         for neighbor_node in self.neighbours(current_node):
#             new_cost = costs[current_node] + self.edge_length(
#                 current_node, neighbor_node
#             )
#             estimated_cost = h(neighbor_node, dest)
#             total_cost = f(new_cost, estimated_cost)

#             if neighbor_node not in closed_set:
#                 if neighbor_node not in costs or new_cost < costs[neighbor_node]:
#                     costs[neighbor_node] = new_cost
#                     heapq.heappush(open_set, (total_cost, neighbor_node))
#                     parents[neighbor_node] = current_node

#     raise Exception("No path found")

# def a_star_search(self, src, dest):
#     def f(cost, heuristic):
#         return cost + heuristic

#     def h(n1, n2):
#         return self.distance(n1, n2)

#     return self.best_first_search(src, dest, f, h)

# def greedy_search(self, src, dest):
#     def f(cost, heuristic):
#         return heuristic

#     def h(n1, n2):
#         return self.distance(n1, n2)

#     return self.best_first_search(src, dest, f, h)

# def uniform_cost_search(self, src, dest):
#     def f(cost, heuristic):
#         return cost

#     def h(n1, n2):
#         return self.distance(n1, n2)

#     return self.best_first_search(src, dest, f, h)
