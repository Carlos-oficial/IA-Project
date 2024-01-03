import uuid
from typing import *

from ia.drivers.veichle import Veichle
from ia.map.map import Map
from ia.map.place import Place
from ia.map.road import Road
from ia.orders.products import *
from ia.map.search import *


class OrderWrapper:
    def __init__(self, order: Order):
        self.order: Order = order


class Driver:
    _id = 0

    def __init__(self, name, veichle, map, initial_node) -> None:
        self.id = Driver._id
        Driver._id += 1
        self.name: str = name
        self.map: Map = map
        self.to_go: List[int] = []
        self.pseudo_route: List[int] = []
        self.curr_node = initial_node
        self.curr_edge: Tuple[int, int] = None  # (u,v)
        self.curr_road: Road = None
        self.curr_order: Order = None
        self.time_left_upper_bound = 0
        self.warehouses: Dict[Warehouse, int] = None
        self.progress_along_edge: float = 0.0
        self.cargo: {Product: int} = dict()
        self.veichle: Veichle = veichle
        self.ratings: List[float] = []
        self.going_path = list()
        self.last_search = None
        self.current_order: Order = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""Driver(id={self.id}, name={self.name},
            vehicle={self.veichle}, ratings={self.ratings},
            current_road={self.curr_road}, location={self.curr_edge}, progress={self.progress_along_edge}
            """ + (
            f"aka {self.map._node_names[self.curr_edge[0]],self.map._node_names[self.curr_edge[1]]})\n"
            if self.curr_edge is not None
            else "\n" "" + f"{self.get_avg_rating()}"
        )

    def get_avg_rating(self):
        if not len(self.ratings):
            return 5
        return sum(self.ratings) / len(self.ratings)

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

    def calc_order_path(self, order: Order):
        warehouse_nodes = {
            tuple(self.warehouses[x] for x in w)
            for w in self.where_to_get(order).values()
        }

        search = DeliverySearch(
            self.map,
            lambda x, y: self.map.estimated_time_btwn_points(
                self, order.weight(), x, y
            ),
            AStar(
                self.map,
                h=lambda x, y: self.map.estimated_time_btwn_points(
                    self, order.weight(), x, y
                ),
                cost_function=lambda x, y: self.map.estimated_time_in_road(
                    self, order.weight(), x, y
                ),
            ),
        )
        dest = {p: n for n, p in self.map.places.items()}[order.destination]
        res = search.run(self.curr_node, dest, warehouse_nodes)
        self.last_search = res
        return res

    # def update_path(self,curr_time =self.clock):
    #     pass

    # def go(self, order, driver: Driver, res: SearchResultOnMap):
    #     self.set_pseudo_route(res.pseudo_route)
    #     self.set_path(res.path)
    #     self.curr_order = order
    #     self.warehouses = self.warehouse_points
    #     print(driver, " goin")

    def pickup_products(self, cargo: Dict[Product, int]):
        for product, ammount in cargo.items():
            if self.cargo.get(product):
                self.cargo[product] += ammount
                self.curr_order.products[product] -= ammount
            else:
                self.cargo[product] = ammount
                self.curr_order.products[product] -= ammount

    def set_pseudo_route(self, route):
        self.pseudo_route = route

    def set_path(self, path: List[int]):
        self.to_go = path
        path_edges = list(zip(path[:-1], path[1:]))
        self.time_left_upper_bound = 0.0
        for u, v in path_edges:
            self.time_left_upper_bound += self.map.estimated_time_in_road(
                self, self.current_order.weight(), u, v
            )

        self.time_left_upper_bound *= 1.1
        u, v = list(path_edges)[0]
        self.curr_road = self.map.roads_mapped[u][v]
        self.curr_edge = u, v
        self.progress_along_edge = 0.0

    def advance(self, sym_time, seconds=1) -> bool:
        self.time_left_upper_bound -= seconds
        u, v = self.curr_edge
        self.curr_road = self.map.roads_mapped[u][v]
        road_max_speed = self.curr_road.max_speed()
        veichle_max_speed = self.veichle.calc_max_velocity(
            cargo=sum(self.cargo.values())
        )

        speed = min(road_max_speed, veichle_max_speed)
        distance = speed / 3.6
        self.progress_along_edge += distance
        road_len = self.curr_road.length

        time_left = (
            self.map.estimated_time_in_path(self.to_go, max_speed=veichle_max_speed)
            - self.progress_along_edge * 3.6 / veichle_max_speed
        )
        if self.progress_along_edge >= road_len:
            self.progress_along_edge = 0.0
            self.curr_node = self.to_go.pop(0)
            print(self.map._node_names[self.curr_node])
            if len(self.to_go) <= 1:
                self.curr_node = self.to_go[-1]

                def show_time(time):
                    return f"{int(time/3600)}:{int(time/60)}:{int(time%60)}"

                self.add_rating(
                    input(
                        f"era suposto chegar{show_time(self.curr_order.time_limit)}, chegou {show_time(sym_time)} quantas estrelas?"
                    )
                )
                return True
            # avança de estrada
            u, v = self.to_go[0], self.to_go[1]
            self.curr_edge = u, v
            if self.curr_node == self.pseudo_route[0]:
                self.pseudo_route.pop(0)
                w = {
                    node: warehouse for warehouse, node in self.warehouses.items()
                }.get(self.curr_node)
                if w:  # at a warehouse
                    keys_to_remove = []

                    for product, amount in self.curr_order.products.items():
                        if product in w.products.values():
                            self.cargo[product] = amount
                            keys_to_remove.append(product)

                    # Remove the keys after the iteration
                    for key in keys_to_remove:
                        self.curr_order.products.pop(key)

            if time_left > self.time_left_upper_bound:
                print(self.map._node_names[self.curr_node])
                self.to_go = self.calc_order_path(self.curr_order).path
                new_time = time_left
                self.time_left_upper_bound = new_time * 1.1

            if len(self.to_go) <= 1:
                self.curr_node = self.to_go[-1]

                def show_time(time):
                    return f"{int(time/3600)}:{int(time/60)}:{int(time%60)}"

                self.add_rating(
                    input(
                        f"era suposto chegar{show_time(self.curr_order.time_limit)}, chegou {show_time(sym_time)} quantas estrelas?"
                    )
                )
                return True

            u, v = self.to_go[0], self.to_go[1]
            self.curr_road = self.map.roads_mapped[u][v]
            self.curr_edge = u, v
            self.curr_node = self.curr_edge[0]

        return False

    def add_rating(self, rating):
        self.ratings.append(rating)
