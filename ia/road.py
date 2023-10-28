from ia.place import Place


class Road:
    def __init__(self, src, to, length):
        self.src: Place = src
        self.to: Place = to
        self.length = length
        self.open = True

    def vel_cap(self):
        if not self.open:
            return 0
        else:
            return 50

    def get_destination(self):
        return self.to

    def get_source(self):
        return self.src


class FreeWay(Road):
    pass


class FastQuickWay(Road):
    pass
