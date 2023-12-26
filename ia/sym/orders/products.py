import json
import uuid
from typing import Any, Dict, List, Set

from ia.sym.map.place import Place


class Product:
    names: Dict[str, Any] = dict()

    def __init__(self, name: str, weight: float):
        if name not in Product.names.keys():
            self.weight: float = weight
            self.name: str = name
            Product.names[name] = self
        else:
            self = Product.names[name]

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
    def __init__(self, time: int, place: Place, products: Set[Product]):
        self.id = uuid.uuid1()
        self.time: int = time
        self.destination: Place = place
        self.products = set()
        self.to_visit_places = set()
        self.status = 0

    def set_rating(self, rating):
        if not self.delivered:
            self.rating = rating

    def restart_order(self):
        self.products.clear
        self.status = 0

    def ask_delivery(self):
        self.done = 1

    def deliver(self):
        self.delivered = 2

    def next_status(self, status):
        if self.status <= 0:
            self.status = 0

        self.status = self.status + 1

        if self.status >= 2:
            self.status = 2

    def add_places_to_visit(self, place):
        self.to_visit_places.add(place)
