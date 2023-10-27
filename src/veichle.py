class Veichle:
    def __init__(self, velocity_cap, avg_velocity, weight_cap, vel_decrement):
        self.velocity_cap = velocity_cap
        self.avg_velocity = avg_velocity
        self.weight_cap = weight_cap
        self.vel_decrement = vel_decrement
        self.cargo = {}

    def cargo_weight(self):
        return 0

    def calc_velocity(self):
        return self.avg_velocity - self.cargo_weight() * self.vel_decrement


class Car(Veichle):
    def __init__(self):
        super().__init__(self, 50, 50, 100, 0.1)


class Bike(Veichle):
    def __init__(self):
        super().__init__(self, 35, 35, 20, 0.5)


class Bycicle(Veichle):
    def __init__(self):
        super().__init__(self, 10, 10, 5, 0.6)
