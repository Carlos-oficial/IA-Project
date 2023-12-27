import time

from ia.sym.map.map import Map
from ia.sym.orders.products import Product

from typing import *


class Simulation:
    start_time = (8, 0, 0)
    start_date = (2023, 12, 25)

    class Dificulty:
        EASY = "easy"
        NORMAL = "normal"

    def __init__(self, map, veichles):
        self.difficulty = None
        self.clock: int = 0
        self.map = map
        self.veichles = veichles

    def __repr__(self):
        h, m, s = Simulation.start_time
        return f"""
time: {h + int(self.clock / 3600)}:{m + int(self.clock / 60) % 12}:{s + self.clock % 60}
              """

    def tick(self, n=1):
        self.clock += n

    def order(client_node, products: Dict[Product, int]):
        pass

    def skip(self, ticks: int):
        for i in range(0, ticks):
            self.tick()

    def start(self):
        commands = {"tick": self.tick}
        while True:
            command = input("Insira comando: ")
            toks = command.split(" ")
            if toks[0] in commands.keys():
                command = commands[toks[0]]
                command(*toks[1:])
            print(self)

    # def place_order()
