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
        self.progress_along_edge: float = 0.0
        self.cargo: {Product: int} = dict()
        self.veichle: Veichle = veichle
        self.ratings: List[float] = 0
        self.going_path = list()
        self.current: Order = None

    def __repr__(self):
        return (
            f"Driver(id={self.id}, name={self.name}, "
            f"vehicle={self.veichle}, ratings={self.ratings}, "
            f"current_road={self.curr_road}, location={self.curr_edge}"
            + f" aka {self.map._node_names[self.curr_edge[0]],self.map._node_names[self.curr_edge[1]]})"
            if self.curr_edge is not None
            else ""
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
        distance = 3.6 * speed
        self.progress_along_edge += distance
        road_len = self.curr_road.length
        if self.progress_along_edge >= road_len:
            self.progress_along_edge = 0.0
            node = self.to_go.pop(0)
            if node == self.pseudo_route[0]:
                self.pseudo_route.pop(0)
                w: Warehouse = {
                    node: warehouse
                    for warehouse, node in self.map.pickup_points.items()
                }.get(node)
                if w:  # at a warehouse
                    for product, ammount in self.curr_order.products.items():
                        if product in w.products.values():
                            self.cargo[product] = ammount
                            self.curr_order.products.pop(product)
            if not self.to_go:
                True
            u, v = self.to_go[0], self.to_go[1]
            self.curr_road = self.map.roads_mapped[u][v]
            self.curr_edge = u, v
            self.progress_along_edge -= road_len
        return False

    def add_rating(self, rating):
        self.ratings.append(rating)
