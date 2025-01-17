import matplotlib.pyplot as plt
import osmnx as ox

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import *
from ia.ui.map_generator import MapGenerator, MapGeneratorState

# s = MapGenerator.run()
s = MapGeneratorState.load_from_file("Gualtar")
m = Map.from_map_gen_state(s)


center = m.central_node()
j = Driver("Júlio", Bike(), m, center)
c = Driver("Carlos", Bike(), m, center)
dirvers = {
    j: center,
    c: center,
    Driver("Gerson", Car(), m, center): center,
    Driver("Filipe", Bycicle(), m, center): center,
}


s = Simulation(m, dirvers, warehouses=s.warehouses)
s.difficulty = Simulation.Dificulty.NORMAL

d = {p.name: p for p in s.products}
d["Pao"]
order = Order(s.clock, s.clock + 300, s.places["HI"], {d["Pao"]: 2, d["Carne"]: 1})
s.pending_orders.append(order)
s.skip(50)
s.plot_driver_command(c)


# A = m.get_node_by_name("A")
# CO = m.get_node_by_name("CO")
# print(s.estimated_time_btwn_points(j, order, A, CO))
