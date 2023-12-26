import time

from ia.sym.map.map import Map
from ia.sym.catalog import Catalog


class Simulation:
    class State:
        start_time = (8, 0, 0)
        start_date = (2023, 12, 25)

        def __init__(self):
            self.clock: int = 0

        def tick(self):
            self.clock += 1

        def __repr__(self):
            h, m, s = State.start_time
            print(
                h + int(self.clock / 3600),
                m + int(self.clock / 60) % 12,
                s + self.clock % 60,
            )

    class Dificulty:
        EASY = "easy"
        NORMAL = "normal"

    def __init__(self, map):
        self.state = Simulation.State()
        self.difficulty = None
        self.facade = Connection.new()

    def start(self):
        while True:
            command = input("Insira comando")
        pass

    # def place_order()

    def tick(self):
        self.state.tick()
