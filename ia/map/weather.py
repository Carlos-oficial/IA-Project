from enum import Enum
import random


class Weather(Enum):
    Sunny = 1
    Cloudy = 2
    Rainy = 3
    Mist = 4

    @staticmethod
    def randomize():
        return random.choice(list(Weather))
