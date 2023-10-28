class Product:
    names = []

    def __init__(self, name, weight):
        self.weight = weight
        if name not in Product.names:
            self.name = name
            self.id = hash(name)
        else:
            raise Exception("Product already exists")

    def set_price(self):
        return 0
