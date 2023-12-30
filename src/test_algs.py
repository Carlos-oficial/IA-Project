import matplotlib.pyplot as plt
import osmnx as ox

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import Simulation
from ia.ui.map_generator import MapGenerator, MapGeneratorState

# s = MapGenerator.run()


map = Map("Gualtar, PT", "file")
map.fetch_map()


AA = map.get_node_by_name("AA")
GG = map.get_node_by_name("GG")
AJ = map.get_node_by_name("AJ")
GA = map.get_node_by_name("GA")
HI = map.get_node_by_name("HI")


alg = GreedySearch(map, map.distance)
route_alg = RestrictedTourSearch(map, map.distance, alg)
res = route_alg.run(AA, {GG, AA}, {GG: {AA}})
print(res)
res.plot()

# AA AJ GA GG HI
