from typing import Dict

from ia.map.weather import Weather


class Place:
    def __init__(self, name: str, x=None, y=None):
        self.name = name
        self.x = x
        self.y = y
        self.storage: Dict[str, int] = {}
        self.weather: Weather = Weather.randomize()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def get_weather(self) -> Weather:
        return self.weather
