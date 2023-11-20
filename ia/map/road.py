from ia.place import Place


class Road:
    def __init__(self, src, to, length) -> None:
        self.src: Place = src
        self.to: Place = to
        self.length: float = length
        self.open: bool = True
        
        src-weather = get_weather(src)
        to-weather = get_weather(to)
        weather = random.choice(src-weather, to-weather)

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
