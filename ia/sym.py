from ia.map.map import Map


class Simulation:
    class State:
        def __init__(self):
            self.clock: int = 0

        def tick(self):
            self.clock += 1

    class Dificulty:
        EASY = "easy"
        NORMAL = "normal"

    def __init__(self):
        self.state = Simulation.State()
        self.difficulty = None
        self.map = Map()
        self.drivers = dict({})
        self.orders = dict({})

    def run():
        self.tui
