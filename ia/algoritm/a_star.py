from queue import PriorityQueue
from typing import List
from ia.map.place import Place
from ia.map.map import Map
from ia.drivers.veichle import Veichle

class A_Star():

    def search(self, graph: Map, veichle: Veichle, start: Place, end: Place, path: List[Place]):
        # getEstimated = lambda x: x.getEstimated(veichle)
        queue = PriorityQueue()
        parents = {}
        visited = set()
        # Priority queue element: (total_cost, node)
        queue.put((0, start))
        parents[start] = None

        while not queue.empty():
            current_cost, current_node = queue.get()

            if current_node == end:
                # Reached the destination, reconstruct the path
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = parents[current_node]
                return list(reversed(path))

            if current_node in visited:
                continue

            visited.add(current_node)

            for neighbor_road in graph.get_neighbours(current_node):
                neighbor_node = neighbor_road.to

                # Calculate the cost from start to the neighbor through the current node
                new_cost = current_cost + neighbor_road.length

                # TODO: Add your heuristic (estimated cost) function here
                # estimated_cost = getEstimated(neighbor_node)
                # total_cost = new_cost + estimated_cost

                if neighbor_node not in visited:
                    if neighbor_node not in parents or new_cost < parents[neighbor_node]:
                        # Update the cost and add to the priority queue
                        parents[neighbor_node] = new_cost
                        queue.put((new_cost, neighbor_node))

        # If the queue is empty and we haven't reached the destination, there is no path
        raise Exception("No path found")


        