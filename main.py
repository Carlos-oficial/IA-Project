import matplotlib.pyplot as plt
import osmnx as ox

from ia.sym.map.map import Map
from ia.sym.map.search import *
from ia.ui.map_generator import MapGenerator, MapGeneratorState

# s = MapGenerator.run()
# map = Map.from_map_gen_state(s)

map = Map("Gualtar, PT", "file")
map.fetch_map()
# map.plot(    )

s = map.get_node_by_name("AA")
n1 = map.get_node_by_name("GG")
n2 = map.get_node_by_name("AJ")
n3 = map.get_node_by_name("GA")

alg = AStar(map, map.distance)
route_alg = TourSearch(map, map.distance, alg)
res = route_alg.run(s, n1, n2, n3)
res.plot()

# map.test_distances()
if False:
    while True:
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

    print(res["route"], len(res["explored"]))
