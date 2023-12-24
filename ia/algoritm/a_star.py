import heapq
from queue import PriorityQueue
from typing import List

from ia.map.map import Map
from ia.map.place import Place

# from ia.drivers.veichle import Veichle


def a_star_search(graph: Map, start_: Place, end_: Place) -> List[int]:
    """Método A*

    Args:
        graph (Map): Mapa
        start (int): onde começar
        end (int): onde acabar

    Raises:
        Exception: se não for possivel

    Returns:
        List[int]: lista dos nodos percorridos entetre o start e end
    """
    start = start_
    end = end_
    open_set = [(0, start)]
    closed_set = set()
    parents = {}
    costs = {}

    heapq.heappush(open_set, (0, start))
    parents[start] = None
    costs[start] = 0

    while open_set:
        current_cost, current_node = heapq.heappop(open_set)

        print(f"Processing node: {current_node} {current_node.name}")

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
            new_cost = costs[current_node] + neighbor_road.length
            estimated_cost = neighbor_road.max_speed_heuristic()
            total_cost = new_cost + estimated_cost

            if neighbor_node not in closed_set:
                if neighbor_node not in costs or new_cost < costs[neighbor_node]:
                    costs[neighbor_node] = new_cost
                    heapq.heappush(open_set, (total_cost, neighbor_node))
                    parents[neighbor_node] = current_node
                    print(
                        f"Adding {neighbor_node.name} to queue with cost {new_cost}, total cost {total_cost}"
                    )

    raise Exception("No path found")
