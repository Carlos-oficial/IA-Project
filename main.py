import matplotlib.pyplot as plt
import osmnx as ox

from ia.sym.map.map import Map
from ia.sym.drivers.driver import Driver
from ia.sym.drivers.veichle import *
from ia.sym.map.search import *
from ia.sym.sym import Simulation
from ia.sym.ui.map_generator import MapGenerator, MapGeneratorState

s = MapGeneratorState.load_from_file("Gualtar")
# s = MapGenerator.run()
map = Map.from_map_gen_state(s)
nodes = list(map.graph.nodes)

dirvers = {
    Driver("Júlio", Bike()): random.choice(nodes),
    Driver("Carlos", Bike()): random.choice(nodes),
    Driver("Gerson", Car()): random.choice(nodes),
    Driver("Filipe", Bycicle()): random.choice(nodes),
}

s = Simulation(map, dirvers, warehouses=s.warehouses)
s.start()

# map = Map("Gualtar, PT", "file")
# map.fetch_map()
# map.proportion = get_proportion(map, map.distance, n=5000)
# print("Proportion is", map.proportion)
#


# AA = map.get_node_by_name("AA")
# GG = map.get_node_by_name("GG")
# AJ = map.get_node_by_name("AJ")
# GA = map.get_node_by_name("GA")
# HI = map.get_node_by_name("HI")


# alg = AStar(map, map.distance)
# route_alg = RestrictedTourSearch(map, map.distance, alg)
# res = route_alg.run(AA, set([GG, AJ, GA, HI]), {GG: {AJ, GA}})
# print(res)
# res.plot()

# map.plot(highlight=set([AA, GG, AJ, GA, HI]))

# AA AJ GA GG HI
