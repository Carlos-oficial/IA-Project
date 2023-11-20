from typing import Dict
from Weather


class Place:
    def __init__(self, name: str):
        self.name = name
        self.storage: Dict[str, int] = {}
        self.weather = weather.randomize()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def get_weather(self):
        return self.weather
