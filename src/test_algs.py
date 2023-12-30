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
# map.plot()


A = map.get_node_by_name("A")
CO = map.get_node_by_name("CO")
FY = map.get_node_by_name("FY")
IG = map.get_node_by_name("IG")
HI = map.get_node_by_name("HI")


alg = AStar(map, map.distance)
route_alg = AndOrRestrictedTourSearch(map, map.distance, alg)
route_alg2 = DeliverySearch(map, map.distance, alg)

# res1 = route_alg.run(A, {IG, A}, {HI:{},IG: {A,(CO,FY)}})
# res1.plot()
res2 = route_alg2.run(A, IG, {A, HI, (CO, FY)})
res2.plot()
# res.plot()
# AA AJ GA GG HI
