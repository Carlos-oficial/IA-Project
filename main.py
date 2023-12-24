from ia.map.map import Map
from ia.ui.map_generator import MapGenerator, MapGeneratorState
import osmnx as ox
import matplotlib.pyplot as plt

s = MapGenerator.run()
map = Map.from_map_gen_state(s)
# g = MapGeneratorState.retrieve_map("Gualtar, PT")
# map = Map.from_ox_graph(g)

print(map.pickup_points)
from ia.algoritm.a_star import a_star_search

src = input("from?")
dest = input("to?")
if src in map.pickup_points.keys():
    source = map.pickup_points[src]
if dest in map.pickup_points.keys():
    destination = map.pickup_points[dest]

path = a_star_search(map, map.places[source], map.places[destination])
path = [elem.id for elem in path]

fig, ax = ox.plot_graph_route(
    map.networkx_graph, path, route_linewidth=6, node_size=0, bgcolor="k"
)
plt.show()
