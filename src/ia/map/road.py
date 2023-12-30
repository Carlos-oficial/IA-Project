import random

from ia.map.place import Place
from ia.map.weather import Weather


class Road:
    def __init__(self, src, to, length, name="", vel_cap=50) -> None:
        self.name: str = name
        self.src: Place = src
        self.to: Place = to
        self.length: float = length
        self.open: bool = True
        self.vel_cap: int = vel_cap
        self.traffic_level: float = 0
        src_weather = src.get_weather()
        to_weather = to.get_weather()
        self.weather = random.choice([src_weather, to_weather])

    def __repr__(self):
        return f"Road ({self.name}) from {self.src.name} to {self.to.name}, Length: {self.length}, Open: {self.open}, Weather: {self.weather}\n"

    def get_weather_factor(self) -> float:
        if self.weather == Weather.Mist:
            return 0.6
        elif self.weather == Weather.Rainy:
            return 0.8
        else:
            return 1.0  # No impact on speed for other weather conditions

    def get_destination(self) -> Place:
        return self.to

    def get_source(self) -> Place:
        return self.src

    def get_weather(self) -> Weather:
        return self.weather

    def max_speed(self) -> float:
        max_speed = self.vel_cap
        length = self.length
        weather_factor = self.get_weather_factor()
        adjusted_max_speed = max_speed * weather_factor * (1 - self.traffic_level / 2)

        return adjusted_max_speed

    def set_traffic(self, traffic_level, randomize=False, ran=0.2):
        if randomize:
            self.traffic_level = max(
                0, min(1, self.traffic_level + (random.random() - 0.5) * ran)
            )
        else:
            self.traffic_level = traffic_level


class FreeWay(Road):
    pass


class FastQuickWay(Road):
    pass
