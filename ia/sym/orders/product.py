from typing import List


class Product:
    names: List[str] = []

    def __init__(self, name, weight):
        self.weight = weight
        if name not in Product.names:
            self.name = name
        else:
            raise Exception("Product already exists")

    def get_name(self):
        return self.name

    def set_price(self, price):
        if price <= 0:
            self.price = price
        else:
            raise Exception("Invalid  price (Must be above 0)")
