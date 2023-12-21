from ia.drivers.veichle import Veichle
from ia.map.place import Place

class Driver:

    def __init__(self, name, veichle, place) -> None:
        self.name : str = name
        self.veichle : Veichle = veichle
        self.current_place : Place = place
        self.current_rating : float = 0
        self.status = 0 
        self.request : Order = None
        self.orders = Dict(Order)

    def add_rating(self, rating):
        self.current_rating = (self.current_place + rating) / 2

    def set_place(self, place):
        self.current_place = place

    def set_veichle(self, veichle):
        self.veichle = veichle

    def next_status(self, status):
        self.status = self.status + 1
        if self.status >= 2:
            self.status = 2

    