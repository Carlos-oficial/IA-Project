import heapq
from typing import List
from ia.map.place import Place
from ia.map.map import Map

# from ia.drivers.veichle import Veichle


def greedy_search(graph: Map, start: Place, end: Place) -> List[Place]:
    open_set = [(0, start)]
    closed_set = set()
    parents = {}

    heapq.heapify(open_set)
    parents[start] = None

    while open_set:
        _, current_node = heapq.heappop(open_set)

        if current_node == end:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = parents[current_node]
            return list(reversed(path))

        if current_node in closed_set:
            continue

        closed_set.add(current_node)

        for neighbor_road in graph.get_neighbours(current_node):
            neighbor_node = neighbor_road.to

            if neighbor_node not in closed_set:
                heuristic_value = neighbor_road.max_speed_heuristic()
                heapq.heappush(open_set, (heuristic_value, neighbor_node))
                parents[neighbor_node] = current_node

    raise Exception("No path found")
