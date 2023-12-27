import time
import matplotlib.pyplot as plt
import networkx as nx
import traceback
from ia.sym.map.map import Map
from ia.sym.orders.products import *
from ia.sym.drivers.driver import *

from typing import *


class Simulation:
    start_time = (8, 0, 0)
    start_date = (2023, 12, 25)

    class Dificulty:
        EASY = "easy"
        NORMAL = "normal"

    def __init__(self, map: Map, drivers: Dict[Driver, int], warehouses=dict()):
        self.difficulty = None
        self.clock: int = 0
        self.map = map
        self.places: Dict[str, Place] = {
            place.name: place for place in map.places.values()
        }

        self.warehouses = warehouses
        self.products = set()
        for x in [w.products.items() for w in warehouses]:
            self.products.update(set(x))

        self.drivers: Dict[int, Driver] = {
            driver.id: driver for driver in drivers.keys()
        }
        self.drivers_pos: Dict[int, Tuple[int, int]] = dict()
        self.drivers_in_transit: Dict[
            int, [Tuple[Tuple[int, int]], float]
        ] = dict()  # id:((from_id,to_id),meters)
        self.stationary_drivers: Dict[int, int] = drivers  # id:node_id

    def __str__(self):
        h, m, s = Simulation.start_time
        return f"""
time: {h + int(self.clock / 3600)}:{m + int(self.clock / 60) % 12}:{s + self.clock % 60}
              """

    def __repr__(self):
        return self.__str__()

    def tick(self, n=1):
        self.clock += int(n)

    def order(client_node, products: Dict[Product, int]):
        pass

    def skip(self, ticks: int):
        for i in range(0, ticks):
            self.tick()

    def plot_command(self, *args):
        lables = len(set(args).intersection("l", "lables"))
        self.plot(show_lables=lables)

    def plot(self, show_lables=False) -> None:
        fig, ax = self.map.plot(
            show_node_lables=show_lables,
            show=False,
            highlight=self.stationary_drivers.values(),
        )
        nx.draw_networkx_labels(
            self.map.graph,
            pos=self.map._render_positions,
            labels={
                node: self.drivers[driver.id].name
                for driver, node in self.stationary_drivers.items()
            },
            bbox=dict(facecolor="white", alpha=0.5),
            font_color="r",
            font_size=10,
            font_weight="bold",
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )
        ax.set_title(self)
        plt.show()

    def start(self):
        commands = {
            "tick": self.tick,
            "plot": self.plot_command,
            "order": self.place_order_command,
        }
        while True:
            try:
                command = input("Insira comando: ")
                toks = command.split(" ")
                command = commands[toks[0]]
                command(*toks[1:])
            except Exception as e:
                print(e.__class__, e)
                traceback.print_exc()

            print(self)

    def place_order_command(
        self,
        time_limit: int,
    ):
        """_summary_

        Args:
            time_limit (int): tempo limite para o pedido
        """
        order_place = input("Onde está? ")
        print(self.places[order_place])

        d = {i: (x, y) for i, (x, y) in enumerate(list(self.products))}
        print(
            "\nProdutos: \n", *[f"\t{i}: {x}:{y.weight}\n" for i, (x, y) in d.items()]
        )

        choices = input(f"O que quer encomendar? [0 .. {len(d)-1}]: ")
        choice_list = choices.split(" ")
        choice_number_list = [int(x) for x in choice_list]

        order = Order(
            self.clock + int(time_limit) * 60,
            self.places[order_place],
            {d[i] for i in choice_number_list},
        )
        print(order.__dict__)
