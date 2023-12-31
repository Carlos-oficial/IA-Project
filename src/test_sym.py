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
map = Map.from_map_gen_state(s)

center = map.central_node()

dirvers = {
    Driver("Júlio", Bike(), map): center,
    Driver("Carlos", Bike(), map): center,
    Driver("Gerson", Car(), map): center,
    Driver("Filipe", Bycicle(), map): center,
}


s = Simulation(map, dirvers, warehouses=s.warehouses)
s.difficulty = Simulation.Dificulty.NORMAL
"""
        order_place = input("Onde está? ")

        d = {i: product for i, product in enumerate(list(self.products))}
        print(
            "\nProdutos: \n", *[f"\t{i}: {x.name}:{x.weight}\n" for i, x in d.items()]
        )

        choices = input(f"O que quer encomendar? [0 .. {len(d)-1}]: ")
        choice_list = choices.split(" ")
        choice_number_list = [int(x) for x in choice_list]

        time_limit = input("em quantos minutos? ")

        order = Order(
            self.clock + int(time_limit) * 60,
            self.places[order_place],
            {d[i]: choice_number_list.count(i) for i in choice_number_list},
        )

        print("it weighs ", order.weight(), " kgs")
        self.pending_orders.append(order)

"""
d = {p.name: p for p in s.products}
d["Pao"]
s.pending_orders.append(
    Order(s.clock + 300, s.places["HI"], {d["Pao"]: 2, d["Carne"]: 1})
)
s.tick()
