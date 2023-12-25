import random

from ia.map.place import Place
from ia.map.weather import Weather


class Road:
    def __init__(self, src, to, length, name="") -> None:
        self.name: str = name
        self.src: Place = src
        self.to: Place = to
        self.length: float = length
        self.open: bool = True

        src_weather = src.get_weather()
        to_weather = to.get_weather()
        self.weather = random.choice([src_weather, to_weather])

    def __repr__(self):
        return f"Road ({self.name}) from {self.src.name} to {self.to.name}, Length: {self.length}, Open: {self.open}, Weather: {self.weather}\n"

    def vel_cap(self) -> float:
        if not self.open:
            return 0
        else:
            return 50

    def get_max_speed(self) -> float:
        return self.vel_cap()

    def get_weather_factor(self) -> float:
        if self.weather == Weather.Mist:
            return 0.5
        elif self.weather == Weather.Rainy:
            return 0.8
        else:
            return 1.0  # No impact on speed for other weather conditions

    def max_speed_heuristic(self) -> float:
        max_speed = self.get_max_speed()
        length = self.length
        weather_factor = self.get_weather_factor()

        # Calculate time using maximum speed
        adjusted_max_speed = max_speed * weather_factor
        time = length / adjusted_max_speed

        return time

    def get_destination(self) -> Place:
        return self.to

    def get_source(self) -> Place:
        return self.src

    def get_weather(self) -> Weather:
        return self.weather


class FreeWay(Road):
    pass


class FastQuickWay(Road):
    pass
