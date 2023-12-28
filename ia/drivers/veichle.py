class Veichle:
    def __init__(
        self, velocity_cap, avg_velocity, weight_cap, vel_decrement, emissions
    ):
        self.velocity_cap = velocity_cap
        self.avg_velocity = avg_velocity
        self.weight_cap = weight_cap
        self.vel_decrement = vel_decrement
        self.cargo: Dict[Product, int] = dict({})  # Mapeia produtos e quantidades
        self.emissions = emissions

    def cargo_weight(self):
        return 0

    def calc_max_velocity(self):
        return self.avg_velocity - self.cargo_weight() * self.vel_decrement


class Car(Veichle):
    """
    "This (assuming fuel economy is 22 miles per gallon), equates to 404g of CO2 for every mile driven.4" de
    https://8billiontrees.com/carbon-offsets-credits/how-much-co2-does-a-car-emit-per-mile/
    emissions ~ 404/1.6 = 251 gramas de CO2 por Km
    """

    def __init__(self):
        super().__init__(50, 50, 100, 0.1, 0.251)


class Bike(Veichle):
    """
    "Medium bike: 0.10086kgCO2/Km" de
    https://thrustcarbon.com/insights/how-to-calculate-motorbike-co2-emissions
    """

    def __init__(self):
        super().__init__(35, 35, 20, 0.5, 0.1)


class Bycicle(Veichle):
    def __init__(self):
        super().__init__(10, 10, 5, 0.6, 0)
