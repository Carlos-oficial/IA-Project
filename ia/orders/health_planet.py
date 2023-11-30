from ia.map.place import Place
from ia.map.map import Map
from ia.orders.product import Product
from typing import Dict, Set
from typing_extensions import TypedDict
import networkx as nx


class HealthPlanet:
    Wharehouse = TypedDict("Wharehouse", {"place": Place, "products": Set[Product]})

    def __init__(self, map: Map):
        self.map: Map = map
        self.wharehouses: Dict[str, HealthPlanet.Wharehouse] = dict({})
        self.selling_products: Dict[str, Product] = dict({})

    def register_product(self, product: Product, *wharehouses):
        self.selling_products[product.name] = product
        for wharehouse in wharehouses:
            self.wharehouses[wharehouse]["products"].add(product)

    def add_warehouse(self, place_name, products: set[Product]):
        try:
            place: Place = self.map.get_place(place_name)
            self.wharehouses[place_name] = {"place": place, "products": products}
            for product in products:
                self.register_product(product)
        except Exception as e:
            print(e, f"in {self}.add_warehouse({place_name, products: set[Product]})")
        finally:
            return

    def _wharehouses_with_product(self, product_name: str):
        p = self.selling_products[product_name]
        return [
            wharehouse["place"]
            for wharehouse in self.wharehouses.values()
            if p in wharehouse["products"]
        ]

    def order_product(self, client_place: str, product_name, ammount: int = 1):
        try:
            self.map.get_place(client_place)
            # order_wheight:float = product.weight*ammount
            src = self._wharehouses_with_product(product_name)[0]
            print(self.map.calculate_path(src.name, client_place))

        except Exception as e:
            print(e, f"in {self}.order_product({client_place: str, product_name: str})")
        finally:
            return
        pass

    def order_products(self, client_place: str, products: dict[Product, int]):
        pass
