import State
import Map

class Simulator:

    def __init__(self, difficulty):
        self.state = State()
        self.difficulty = difficulty
        self.map = Map()
        self.drivers = Dict()
        self.orders = Dict()


