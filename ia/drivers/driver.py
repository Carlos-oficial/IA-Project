from ia.drivers.veichle import Veichle
from ia.map.place import Place

class Driver:

    def __init__(self, name, veichle, place) -> None:
        self.name : str = name
        self.veichle : Veichle = veichle
        self.current_place : Place = place
        self.current_rating : float = 0

    def add_rating(self, rating):
        self.current_rating = (self.current_place + rating) / 2

    def set_place(self, place):
        self.current_place = place

    def set_veichle(self, veichle):
        self.veichle = veichle

    def get_place(self) -> Place:
        return self.current_place
 