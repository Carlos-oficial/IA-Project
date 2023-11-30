import random
from ia.map.place import Place
from ia.map.weather import Weather


class Road:
    def __init__(self, src, to, length) -> None:
        self.src: Place = src
        self.to: Place = to
        self.length: float = length
        self.open: bool = True
        
        src_weather = src.get_weather()
        to_weather = to.get_weather()
        self.weather = random.choice([src_weather, to_weather])

    def vel_cap(self) -> float:
        if not self.open:
            return 0
        else:
            return 50

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
