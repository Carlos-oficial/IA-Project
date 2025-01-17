import time
import traceback
from enum import Enum
from typing import *

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox

from ia.drivers.driver import *
from ia.map.map import Map
from ia.map.search import *
from ia.map.weather import Weather
from ia.orders.products import *


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
        self.pending_orders: List[Order] = []
        self.orders_in_progress: List[Order] = []
        for x in [w.products.values() for w in warehouses]:
            self.products.update(set(x))

        self.drivers: Dict[int, Driver] = {
            driver.id: driver for driver in drivers.keys()
        }
        for driver in drivers.keys():
            driver.warehouses = self.warehouse_points
        self.drivers_in_transit: List[Driver] = list()  # id:((from_id,to_id),meters)
        self.available_drivers: Dict[Driver, int] = drivers  # id:node_id

    def __str__(self):
        h, m, s = Simulation.start_time
        return f"time: {h + int(self.clock / 3600)}:{m + int(self.clock / 60) % 12}:{s + self.clock % 60}"

    def __repr__(self):
        return self.__str__()

    def tick(self, n=1):
        self.clock += int(n)
        self.pending_orders = sorted(self.pending_orders, key=lambda x: x.time_limit)
        for order in self.pending_orders:
            try:
                self.dispatch_order(order)
            except Exception as e:
                print(e)
                traceback.print_exc()
            else:
                self.pending_orders.remove(order)
                self.orders_in_progress.append(order)

        for driver in self.drivers_in_transit:
            self.update_driver(driver, time_passed=n)

    def update_driver(self, driver: Driver, time_passed: int = 1):
        if driver.advance(self.clock, seconds=time_passed):
            self.drivers_in_transit.remove(driver)
            self.available_drivers[driver] = driver.curr_edge[1]
            # driver.update_path(curr_time =self.clock)
            self.orders_in_progress.remove(driver.curr_order)
            # self.handle_order_delivered(driver,order)
            self.drivers

    def skip(self, ticks=1):
        for i in range(0, int(ticks)):
            self.tick()

    def orders_command(self):
        print("pending")
        print(*self.pending_orders)
        print("in progress")
        print(*self.orders_in_progress)

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

    def estimated_time_btwn_points(
        self, driver: Driver, order: Order, node1: int, node2: int
    ):
        x1, y1 = self.map._node_positions[node1]
        x2, y2 = self.map._node_positions[node2]

        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        radius_sq = (x1 - xm) ** 2 + (y1 - ym) ** 2

        circle_filter = {
            node
            for node, (X, Y) in self.map._node_positions.items()
            if ((X - xm) ** 2 + (Y - ym) ** 2 <= radius_sq)
        }

        min_max_speed = 50
        for road in self.map.roads:
            if road.src in circle_filter and road.to in circle_filter:
                min_max_speed = min(min_max_speed, road.max_speed())

        return (
            3.6
            * self.map.distance(node1, node2)
            * self.map.factor
            / min(driver.veichle.calc_max_velocity(cargo=order.weight()), min_max_speed)
        )

    def estimated_time_in_road(self, driver, order, x, y):
        road: Road = self.map.roads_mapped[x][y]
        vel = min(
            driver.veichle.calc_max_velocity(cargo=order.weight()), road.max_speed()
        )
        return 3.6 * road.length / vel

    def where_to_get(self, order: Order):
        dispatched_products = set()
        where_to_get = dict()
        for w in self.warehouses:
            can_get = set(order.products.keys()).intersection(set(w.products.values()))
            dispatched_products = dispatched_products.union(can_get)
            for item in can_get:
                if not where_to_get.get(item):
                    where_to_get[item] = tuple([w])
                else:
                    t = where_to_get[item]
                    l = list(t)
                    l.append(w)
                    t = tuple(l)
                    where_to_get[item] = t
        return where_to_get

    def dispatch_order(self, order: Order):
        print("Dispatching", order)
        end_node = order.destination
        end_node = self.map._name_nodes[order.destination.name]

        where_to_get = self.where_to_get(order)
        print("where_to_get", where_to_get)
        order_weight = sum(p.weight * amm for p, amm in order.products.items())
        driver_emissions: Dict[Driver, float] = dict()
        driver_search_result: Dict[Driver, SearchResult] = dict()

        warehouse_nodes = {
            tuple(self.warehouse_points[x] for x in w) for w in where_to_get.values()
        }
        print("warehouse_nodes", warehouse_nodes)

        for driver, node in [
            (driver, node)
            for driver, node in self.available_drivers.items()
            if driver.veichle.weight_cap >= order_weight
        ]:
            search = DeliverySearch(
                self.map,
                lambda x, y: self.estimated_time_btwn_points(driver, order, x, y),
                AStar(
                    self.map,
                    h=lambda x, y: self.estimated_time_btwn_points(driver, order, x, y),
                    cost_function=lambda x, y: self.estimated_time_in_road(
                        driver, order, x, y
                    ),
                ),
            )
            driver.calc_order_path(order)
            where_to_go = warehouse_nodes.union({end_node})

            res = search.run(node, end_node, warehouse_nodes)
            print(f"res = search.run{(node, end_node, warehouse_nodes)}")

            if (
                self.approx_path_time(driver.veichle, order.weight(), res.path)
                <= order.time_limit
            ):
                driver_emissions[driver] = self.path_emissions(driver.veichle, res.path)
                driver_search_result[driver] = res

            print(
                f"""
                    driver:{driver.name}
                    veichle: {driver.veichle.__class__.__name__} 
                    {self.map.path_length(res.path)/1000} km
                    {self.path_emissions(driver.veichle,res.path)}g of CO2 
                    estimated_time: {int(self.approx_path_time(driver.veichle,order.weight(),res.path)/60)}:{int(self.approx_path_time(driver.veichle,order.weight(),res.path))%60}
                    """
            )

        drivers = list(driver_emissions.keys())
        drivers = sorted(drivers, key=lambda x: driver_emissions[x])

        if len(drivers) == 0:
            raise Exception("No available driver")

        self.send_driver(order, drivers[0], res)

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
            self.clock,
            self.clock + int(time_limit) * 60,
            self.places[order_place],
            {d[i]: choice_number_list.count(i) for i in choice_number_list},
        )

        print("it weighs ", order.weight(), " kgs")
        self.pending_orders.append(order)

    def send_driver(self, order: Order, driver: Driver, res: SearchResultOnMap):
        d_node = self.available_drivers[driver]
        self.available_drivers.pop(driver)
        self.drivers_in_transit.append(driver)
        driver.curr_node = d_node
        driver.curr_order = order
        driver.set_pseudo_route(res.pseudo_route)
        driver.current_order = order
        driver.warehouses = self.warehouse_points
        driver.set_path(res.path)
        driver.last_search = res
        print(driver, " goin")

    def traffic_command(self, *args):
        if len(args) == 0:
            print("Usage: traffic <node1> <node2> <traffic_level>")
            return
        node1 = args[0]
        node2 = args[1]
        traffic_level = float(args[2])
        N1 = self.map.get_node_by_name(node1)
        N2 = self.map.get_node_by_name(node2)
        road: Road = self.map.roads_mapped[N1][N2]
        road.set_traffic(traffic_level)
        road: Road = self.map.roads_mapped[N2][N1]
        road.set_traffic(traffic_level)

    def cut_road_command(self, *args):
        node1 = args[0]
        node2 = args[1]
        N1 = self.map.get_node_by_name(node1)
        N2 = self.map.get_node_by_name(node2)
        road: Road = self.map.roads_mapped[N1][N2]
        road.open = not road.open
        road: Road = self.map.roads_mapped[N2][N1]
        road.open = not road.open

    def drivers_command(self):
        print("avalailable")
        for driver in self.available_drivers:
            print(driver)
            print(str(driver.get_avg_rating()) + " estrelas em média")

        print("drivers in transit")
        for driver in self.drivers_in_transit:
            print(driver)
            print(str(driver.get_avg_rating()) + " estrelas em média")

    def plot_driver_command(self, driver: Driver = None):
        if not driver:
            for driver in self.drivers_in_transit:
                print(driver.name, " : ", driver.id)
                print(driver)

            driver_id = input("qual id? ")
            driver: Driver = self.drivers[int(driver_id)]

        search: SearchResultOnMap = driver.last_search
        fig, ax = search.plot(show=False)

        print("uppon plotting driver.curr_edge is", driver.curr_edge)

        if driver.curr_edge:
            edge_labels = {
                driver.curr_edge: driver.name
                + "{:.2f}m".format(driver.progress_along_edge)
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
        plt.show()

    def plot_command(self, *args):
        lables = len(set(args).intersection("l", "lables"))
        vels = len(set(args).intersection("v"))
        self.plot(show_lables=lables, velocities=vels)

    def plot(self, show_lables=False, velocities=False) -> None:
        fig, ax = self.map.plot(
            show_node_lables=show_lables,
            show=False,
            highlight=list(self.available_drivers.values())
            + [
                self.map._name_nodes[order.destination.name]
                for order in self.pending_orders
            ],
        )

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
                self.map._name_nodes[order.destination.name]: f"order{order.id}"
                for order in self.pending_orders
            },
            bbox=dict(facecolor="white", alpha=0.5),
            font_color="r",
            font_size=10,
            horizontalalignment="right",
            verticalalignment="bottom",
            ax=ax,
        )

        nx.draw_networkx_labels(
            self.map.graph,
            pos=self.map._render_positions,
            labels={
                self.map._name_nodes[order.destination.name]: f"order{order.id}"
                for order in self.orders_in_progress
            },
            bbox=dict(facecolor="white", alpha=0.5),
            font_color="y",
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

        edge_labels = {
            driver.curr_edge: driver.name + "{:.2f}m".format(driver.progress_along_edge)
            for driver in self.drivers_in_transit
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

    def help(self):
        descp = {
            "tick - Advances N ticks in time, by default advances one",
            "traffic - Sets the traffic level of a road:",
            "plot - Shows the map (nodes, drivers, warehouses, etc)",
            "order - Adds an order to the sistem",
            "orders - Shows the orders in the sistem",
            "drivers - Shows the drivers in the sistem",
            "driver_plot - Shows the path of the last search of a driver",
            "help - Shows all commands",
            "quit - Exit",
        }
        for c in descp:
            print(c)

    def quit(self):
        print("Exiting sistem ...")

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
            case _:
                self.difficulty = Simulation.Dificulty.HARD
                for road in self.map.roads:
                    road.set_traffic(0.5, randomize=True)
                    road.weather = Weather.Mist
        # end match
        self.ui()

    def ui(self):
        commands = {
            "tick": self.skip,
            "traffic": self.traffic_command,
            "cut": self.cut_road_command,
            "plot": self.plot_command,
            "order": self.place_order_command,
            "orders": self.orders_command,
            "drivers": self.drivers_command,
            "driver_plot": self.plot_driver_command,
            "help": self.help,
            "quit": self.quit,
        }
        while True:
            try:
                command = input("Insira comando: ")
                toks = command.split(" ")
                command = commands[toks[0]]
                command(*toks[1:])
                print("\n\n")
                if toks[0] == "quit":
                    return
            except Exception as e:
                print(e.__class__, e)
                traceback.print_exc()

            print(self)
