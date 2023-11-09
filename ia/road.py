from ia.place import Place


class Road:
    def __init__(self, src, to, length) ->None:
        self.src: Place = src
        self.to: Place = to
        self.length :float= length
        self.open :bool= True

    def vel_cap(self) -> float:
        if not self.open:
            return 0
        else:
            return 50

    def get_destination(self) -> Place:
        return self.to

    def get_source(self) -> Place:
        return self.src


class FreeWay(Road):
    pass


class FastQuickWay(Road):
    pass
