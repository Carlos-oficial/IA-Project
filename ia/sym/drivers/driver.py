from typing import Dict

from ia.drivers.veichle import Veichle
from ia.sym.map.place import Place


class Driver:
    def __init__(self, name, veichle, place) -> None:
        self.name: str = name
        self.veichle: Veichle = veichle
        self.current_place: Place = place
        self.current_rating: float = 0
        self.available: bool = True
        self.trips = dict(Order)
        self.current: Order = None
        self.id = None

    def add_rating(self, rating):
        self.current_rating = (self.current_place + rating) / 2

    def set_place(self, place):
        self.current_place = place

    def set_veichle(self, veichle):
        self.veichle = veichle

    def new_order(self, order: Order):
        self.available = False
        self.current = order

    def set_id(self, id):
        self.id = id

    def finish_order(self):
        self.order.deliver()
        self.trips.add(self.order)
        self.available = False
        self.current = None
