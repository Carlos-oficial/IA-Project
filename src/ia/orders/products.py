import json
import uuid
from typing import Any, Dict, List, Set

import ia
from ia.map.place import Place


class Product:
    names: Dict[str, Any] = dict()

    def __init__(self, name: str, weight: float):
        if name not in Product.names.keys():
            self.weight: float = weight
            self.name: str = name
            Product.names[name] = self
        else:
            self = Product.names[name]

    def __repr__(self):
        return self.name + str(self.weight) + "kg"

    @staticmethod
    def new(name: str, weight: float):
        if name not in Product.names.keys():
            p = Product(name, weight)
            Product.names[name] = p
            return p
        else:
            return Product.names[name]

    @staticmethod
    def products_from_json(filename) -> List["Product"]:
        products = []
        with open(filename, "r") as file:
            data = json.load(file)
            for product_data in data:
                try:
                    product = Product.new(
                        name=product_data["name"], weight=product_data["weight"]
                    )
                    products.append(product)
                except Exception as e:
                    print(f"Error creating product: {e}")

        return products

    @staticmethod
    def write_products_to_json(products: list, filename: str):
        data = [
            {"name": product.name, "weight": product.weight} for product in products
        ]
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)


class Warehouse:
    def __init__(self, name):
        self.name = name
        self.products: Dict[str, Product] = {}

    def add_product(self, product: Product):
        self.products[product.name] = product

    def to_dict(self):
        return {
            "name": self.name,
            "products": {
                name: {"weight": product.weight}
                for name, product in self.products.items()
            },
        }

    @classmethod
    def from_dict(cls, data):
        warehouse = Warehouse(data["name"])
        for name, product_data in data["products"].items():
            warehouse.add_product(Product.new(name=name, weight=product_data["weight"]))
        return warehouse

    def __repr__(self):
        return f"Warehouse(products={self.products})"

    @staticmethod
    def write_warehouses_to_json(warehouses, filename):
        data = [warehouse.to_dict() for warehouse in warehouses]
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def read_warehouses_from_json(filename):
        warehouses = []
        with open(filename, "r") as file:
            data = json.load(file)
            for warehouse_data in data:
                warehouse = Warehouse.from_dict(warehouse_data)
                warehouses.append(warehouse)
        return warehouses


class Order:
    _id = 0

    def __init__(
        self,
        curr_time: int,
        time_limit: int,
        place: Place,
        products: Dict[Product, int],
    ):
        self.id = Order._id
        Order._id += 1
        self.dispatch_time: int = curr_time
        self.time_limit: int = time_limit
        self.destination: Place = place
        self.products: Dict[Product, int] = products

    def weight(self):
        return sum(
            product.weight * ammount for product, ammount in self.products.items()
        )

    def set_rating(self, rating):
        if not self.delivered:
            self.rating = rating

    def __repr__(self):
        h, m, s = ia.START_TIME
        return f"""
order n{self.id}
destination: {self.destination.name} @ {(self.destination.x,self.destination.y)}
products: {self.products}
time limit: {h + int(self.time_limit / 3600)}:{m + int(self.time_limit / 60) % 12}:{s + self.time_limit % 60}
    """

        return f"""
              """
