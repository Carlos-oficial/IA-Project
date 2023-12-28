import time
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import traceback
from ia.map.map import Map
from ia.map.search import *
from ia.map.weather import Weather
from ia.orders.products import *
from ia.drivers.driver import *
import numpy as np
from typing import *
import osmnx as ox
import geopandas as gpd

from enum import Enum


class Simulation:
    start_time = (8, 0, 0)
    start_date = (2023, 12, 25)

    class Dificulty(Enum):
        EASY = "easy"
        NORMAL = "normal"
        HARD = "hard"

    def __init__(self, map: Map, drivers: Dict[Driver, int], warehouses: list):
        self.difficulty = None
        self.clock: int = 0
        self.map = map
        self.places: Dict[str, Place] = {
            place.name: place for place in map.places.values()
        }
        self.warehouses = warehouses
        self.names_warehouses: Dict[str, Warehouse] = {w.name: w for w in warehouses}
        self.warehouse_points = {
            self.names_warehouses[name]: node
            for name, node in map.pickup_points.items()
        }
        self.products = set()
        self.orders: List[Order] = []
        for x in [w.products.values() for w in warehouses]:
            self.products.update(set(x))

        self.drivers: Dict[int, Driver] = {
            driver.id: driver for driver in drivers.keys()
        }
        self.drivers_pos: Dict[int, Tuple[int, int]] = dict()
        self.drivers_in_transit: Dict[
            int, [Tuple[Tuple[int, int]], float]
        ] = dict()  # id:((from_id,to_id),meters)
        self.available_drivers: Dict[Driver, int] = drivers  # id:node_id

    def __str__(self):
        h, m, s = Simulation.start_time
        return f"""
time: {h + int(self.clock / 3600)}:{m + int(self.clock / 60) % 12}:{s + self.clock % 60}
              """

    def __repr__(self):
        return self.__str__()

    def tick(self, n=1):
        self.clock += int(n)
        self.randomize_update_traffic()
        for order in self.orders:
            path = self.get_order_shortest_path(order)

    def approx_path_time(
        self, veichle: Veichle, maxcargo: float, path: List[int]
    ) -> float:
        total_time_seconds = 0.0
        vel = veichle.calc_max_velocity(cargo=maxcargo)
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            total_time_seconds += (
                self.map._edge_length(u, v)
                * 3.6
                / min(self.map.roads_mapped[u][v].max_speed(), vel)
            )
        return total_time_seconds

    def path_emissions(self, veichle: Veichle, path: List[int]) -> float:
        return self.map.path_length(path) / 1000 * veichle.emissions

    def mean_speed(self, driver, node1, node2):
        """
        mean top speed
        """
        min_speed = 50
        max_speed = 0
        for road in self.map.roads:
            min_speed = min(min_speed, road.max_speed())
            max_speed = max(max_speed, road.max_speed())
        return (min_speed + max_speed) / 2

    def estimated_time(self, driver: Driver, order: Order, node1: int, node2: int):
        return (
            3.6
            * self.map.distance(node1, node2)
            * 1.6
            / driver.veichle.calc_max_velocity(cargo=order.weight())
        )

    def dispatch_order(self, order: Order):
        end_node = order.destination
        end_node = self.map._name_nodes[order.destination.name]

        dispatched_products = set()
        where_to_get = dict()
        for w in self.warehouses:
            can_get = set(order.products.keys()).intersection(set(w.products.values()))
            dispatched_products = dispatched_products.union(can_get)
            for item in can_get:
                where_to_get[item] = w
        print(where_to_get)
        order_weight = sum(p.weight * amm for p, amm in order.products.items())
        for driver, node in self.available_drivers.items():
            if driver.veichle.weight_cap > order_weight:
                search = RestrictedTourSearch(
                    self.map,
                    self.map.distance,
                    GreedySearch(
                        self.map,
                        h=lambda x, y: self.estimated_time(driver, order, x, y),
                    ),
                )
                warehouse_nodes = {
                    self.warehouse_points[w] for w in where_to_get.values()
                }
                where_to_go = warehouse_nodes.union({end_node})
                print((node, where_to_go, {end_node: warehouse_nodes}))
                res = search.run(node, where_to_go, {end_node: warehouse_nodes})
                print(
                    f"""
path: {res.path}
veichle: {driver.veichle.__class__.__name__} 
{self.map.path_length(res.path)/1000} km
{self.path_emissions(driver.veichle,res.path)}g of CO2 
estimated_time: {int(self.approx_path_time(driver.veichle,order.weight(),res.path)/60)}min
"""
                )

    def skip(self, ticks: int):
        for i in range(0, ticks):
            self.tick()

    def plot_command(self, *args):
        lables = len(set(args).intersection("l", "lables"))
        vels = len(set(args).intersection("v"))
        self.plot(show_lables=lables, velocities=vels)

    def plot(self, show_lables=False, velocities=False) -> None:
        fig, ax = self.map.plot(
            show_node_lables=show_lables,
            show=False,
            highlight=list(self.available_drivers.values())
            + [self.map._name_nodes[order.destination.name] for order in self.orders],
        )

        midpoints = {
            (u, v): (
                (self.map._render_positions[u][0] + self.map._render_positions[v][0])
                / 2,
                (self.map._render_positions[u][1] + self.map._render_positions[v][1])
                / 2,
            )
            for (u, v), _ in self.drivers_in_transit.values()
        }

        for x, y in midpoints.values():
            # print(x,y)
            plt.scatter(x, y, color="blue", marker="o", s=10)

        nx.draw_networkx_labels(
            self.map.graph,
            pos=self.map._render_positions,
            labels={
                node: self.drivers[driver.id].name
                for driver, node in self.available_drivers.items()
            },
            bbox=dict(facecolor="white", alpha=0.5),
            font_color="r",
            font_size=10,
            font_weight="bold",
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )

        nx.draw_networkx_labels(
            self.map.graph,
            pos=self.map._render_positions,
            labels={
                self.map._name_nodes[order.destination.name]: "order"
                for order in self.orders
            },
            bbox=dict(facecolor="white", alpha=0.5),
            font_color="r",
            font_size=10,
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )

        def color_from(speed):
            # Set the maximum speed
            max_speed = 50.0

            # Normalize the speed to be in the range [0, 1]
            normalized_speed = np.tanh(speed / max_speed)
            normalized_speed = (normalized_speed + 1) / 2
            normalized_speed = speed / max_speed

            # Blend red and green colors based on the normalized speed
            color_tuple = (1.0 - normalized_speed, normalized_speed, 0.0)

            # Convert the RGB values to a hex string
            hex_color = "#{:02X}{:02X}{:02X}".format(
                int(color_tuple[0] * 255),
                int(color_tuple[1] * 255),
                int(color_tuple[2] * 255),
            )

            return hex_color

        edges = self.map.graph.edges()
        edge_traffic = [
            color_from(self.map.roads_mapped[u][v].max_speed()) for (u, v) in edges
        ]

        if velocities:
            edge_labels = {
                (u, v): "{:.1f}km/h".format(self.map.roads_mapped[u][v].max_speed())
                for u, v in edges
            }
            nx.draw_networkx_edge_labels(
                self.map.graph,
                self.map._render_positions,
                edge_labels=edge_labels,
                font_color="w",
                font_size=8,
                bbox=dict(facecolor="red", alpha=0.1),
                ax=ax,
            )

        fig, ax = ox.plot_graph(
            self.map.graph,
            node_size=0,
            edge_color=edge_traffic,
            bgcolor="k",
            show=False,
            ax=ax,
        )

        ax.set_title(self)
        plt.show()

    def start(self):
        difficulty = input("difficulty 0|1|2: ")
        match (difficulty):
            case ("0"):
                self.difficulty = Simulation.Dificulty.EASY
                for road in self.map.roads:
                    road.set_traffic(0, randomize=False)
            case ("1"):
                self.difficulty = Simulation.Dificulty.NORMAL
                for road in self.map.roads:
                    road.set_traffic(0.2, randomize=True)
            case ("2"):
                self.difficulty = Simulation.Dificulty.HARD
                for road in self.map.roads:
                    road.set_traffic(0.5, randomize=True)
                    road.weather = Weather.Mist

        # end match
        self.ui()

    def ui(self):
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
    ):
        """_summary_

        Args:
            time_limit (int): tempo limite para o pedido
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
        self.orders.append(order)
        self.dispatch_order(order)