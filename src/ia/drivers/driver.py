import uuid
from typing import *

from ia.drivers.veichle import Veichle
from ia.map.map import Map
from ia.map.place import Place
from ia.map.road import Road
from ia.orders.products import *


class Driver:
    _id = 0

    def __init__(self, name, veichle, map) -> None:
        self.id = Driver._id
        Driver._id += 1
        self.name: str = name
        self.map: Map = map
        self.to_go: List[int] = []
        self.pseudo_route: List[int] = []
        self.curr_edge: Tuple[int, int] = None  # (u,v)
        self.curr_road: Road = None
        self.curr_order: Order = None
        self.warehouses: Dict[Warehouse, int] = None
        self.progress_along_edge: float = 0.0
        self.cargo: {Product: int} = dict()
        self.veichle: Veichle = veichle
        self.ratings: List[float] = 0
        self.going_path = list()
        self.last_search = None
        self.current: Order = None

    def __str__(self):return self.name

    def __repr__(self):
        return (
            f"""Driver(id={self.id}, name={self.name},
            vehicle={self.veichle}, ratings={self.ratings},
            current_road={self.curr_road}, location={self.curr_edge}, progress={self.progress_along_edge}
            """ +( f"aka {self.map._node_names[self.curr_edge[0]],self.map._node_names[self.curr_edge[1]]})\n"
            if self.curr_edge is not None
            else "\n""")
        )

    def add_cargo(cargo: Dict[Product, int]):
        for product, ammount in cargo.items():
            if self.cargo.get(product):
                self.cargo[product] += ammount
            else:
                self.cargo[product] = ammount

    def set_pseudo_route(self, route):
        self.pseudo_route = route

    def set_path(self, path: List[int]):
        self.to_go = path
        u, v = path[0], path[1]
        self.curr_road = self.map.roads_mapped[u][v]
        self.curr_edge = u, v
        self.progress_along_edge = 0.0

    def advance(self, seconds=1) -> bool:
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
        if self.progress_along_edge >= road_len:
            self.progress_along_edge = 0.0
            node = self.to_go.pop(0)
            if node == self.pseudo_route[0]:
                self.pseudo_route.pop(0)
                w = {
                    node: warehouse
                    for warehouse, node in self.map.pickup_points.items()
                }.get(node)
                w = {
                    node: warehouse for warehouse, node in self.warehouses.items()
                }.get(node)
                if w:  # at a warehouse
                    keys_to_remove = []

                    for product, amount in self.curr_order.products.items():
                        if product in w.products.values():
                            self.cargo[product] = amount
                            keys_to_remove.append(product)

                    # Remove the keys after the iteration
                    for key in keys_to_remove:
                        self.curr_order.products.pop(key)

            if len(self.to_go) <= 1:
                return True
            # avança de estrada
            
            u, v = self.to_go[0], self.to_go[1]
            self.curr_road = self.map.roads_mapped[u][v]
            self.curr_edge = u, v
        return False

    def add_rating(self, rating):
        self.ratings.append(rating)
