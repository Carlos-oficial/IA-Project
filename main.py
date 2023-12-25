import matplotlib.pyplot as plt
import osmnx as ox

from ia.sym.map.map import Map
from ia.sym.map.search import *
from ia.ui.map_generator import MapGenerator, MapGeneratorState

# s = MapGenerator.run()
# map = Map.from_map_gen_state(s)

map = Map("Gualtar, PT", "file")
map.fetch_map()

s = map.get_node_by_name("AA")
d = map.get_node_by_name("GA")
alg = GreedySearch(map, map.distance)
res = alg.run(s, d)
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
