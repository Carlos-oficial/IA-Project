from typing import Dict

from ia.sym.map.weather import Weather


class Place:
    _id = 0

    @staticmethod
    def _new_id():
        id += 1
        return id

    def __init__(self, name: str, x=None, y=None, id=None):
        if id is None:
            self.id = Place._new_id()
        else:
            self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.weather: Weather = Weather.randomize()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"""{self.name} @ {self.x,self.y}
    weather:{self.weather}
    """

    def get_weather(self) -> Weather:
        return self.weather
