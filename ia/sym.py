from ia.state import State
from ia.map.map import Map

class Simulator:

    def __init__(self, difficulty):
        self.state = State()
        self.difficulty = difficulty
        self.map = Map()
        self.drivers = Dict()
        self.orders = Dict()


