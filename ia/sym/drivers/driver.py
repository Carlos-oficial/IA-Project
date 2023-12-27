from typing import *
import uuid
from ia.sym.drivers.veichle import Veichle
from ia.sym.map.place import Place
from ia.sym.orders.products import *


class Driver:
    def __init__(self, name, veichle) -> None:
        self.id = uuid.uuid1()
        self.name: str = name
        self.veichle: Veichle = veichle
        self.ratings: List[float] = 0
        self.available: bool = True
        self.trips = dict()
        self.current: Order = None

    def add_rating(self, rating):
        self.ratings.append(rating)

    def new_order(self, order: Order):
        self.available = False
        self.current = order

    def finish_order(self):
        self.order.deliver()
        self.trips.add(self.order)
        self.available = False
        self.current = None
