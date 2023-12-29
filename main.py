import matplotlib.pyplot as plt
import osmnx as ox

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import Simulation
from ia.ui.map_generator import MapGenerator, MapGeneratorState

# s = MapGenerator.run()
s = MapGeneratorState.load_from_file("Gualtar")
map = Map.from_map_gen_state(s)

center = map.central_node()

dirvers = {
    Driver("Júlio", Bike(), map): center,
    Driver("Carlos", Bike(), map): center,
    Driver("Gerson", Car(), map): center,
    Driver("Filipe", Bycicle(), map): center,
}


s = Simulation(map, dirvers, warehouses=s.warehouses)
s.start()

# map = Map("Gualtar, PT", "file")
# map.fetch_map()
# map.proportion = get_proportion(map, map.distance, n=5000)
# print("Proportion is", map.proportion)


# AA = map.get_node_by_name("AA")
# GG = map.get_node_by_name("GG")
# AJ = map.get_node_by_name("AJ")
# GA = map.get_node_by_name("GA")
# HI = map.get_node_by_name("HI")


# alg = GreedySearch(map, map.distance)
# res = alg.run(GG, AA)
# res.plot()
# route_alg = RestrictedTourSearch(map, map.distance, alg)
# res = route_alg.run(AA, set([GG, AJ, GA, HI]), {GG: {AJ, GA}})
# print(res)
# res.plot()

# map.plot(highlight=set([AA, GG, AJ, GA, HI]))

# # AA AJ GA GG HI
