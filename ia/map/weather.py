import enum as Enum
import random

class Weather(Enum):
    Sunny = 1
    Cloudy = 2
    Rainy = 3
    Mist = 4

    def randomize(self):
        return random.choice(list(Weather))

