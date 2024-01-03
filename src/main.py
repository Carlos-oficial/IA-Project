import matplotlib.pyplot as plt
import osmnx as ox

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import Simulation
from ia.ui.map_generator import MapGenerator, MapGeneratorState

generate = input("Generate? y/n ") == "y"
if generate:
    s = MapGenerator.run()
else:
    s = MapGeneratorState.load_from_file("Gualtar")

map = Map.from_map_gen_state(s)

center = map.central_node()

dirvers = {
    Driver("Júlio", Bike(), map, center): center,
    Driver("Carlos", Bike(), map, center): center,
    Driver("Gerson", Car(), map, center): center,
    Driver("Filipe", Bycicle(), map, center): center,
}


s = Simulation(map, dirvers, warehouses=s.warehouses)
s.start()
