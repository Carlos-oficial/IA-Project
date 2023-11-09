from ia.place import Place
from ia.map import Map
from ia.product import Product
from typing import Dict, Set
import networkx as nx

class HealthPlanet:
    def __init__(self, map: Map):
        self.map: Map = map
        self.wharehouses: Dict[str, Dict[str, Place | Set[Product]]] = {}
        self.selling_products: Dict[str:Product] = {}

    def register_product(self, product: Product, *wharehouses):
        self.selling_products[product.name] = product
        for wharehouses in wharehouses:
            self.wharehouses[wharehouses]["products"].add(product)

    def add_warehouse(self, place_name, products: set[Product]):
        try:
            place: Place = self.map.get_place(place_name)
            self.wharehouses[place_name] = {"place": place, "products": products}
            for product in products:
                self.register_product(product)
            print(self.wharehouses)
        except Exception as e:
            print(e)
        finally:
            return

    def _wharehouses_with_product(self, product_name: str):
        p = self.selling_products[product_name]
        return [
            wharehouse["place"]
            for wharehouse in self.wharehouses.values()
            if p in wharehouse["products"]
        ]
    
     
    def order_product(self, client_place: str, product: Product,ammount:int = 1):
        try:
            place: Place = self.map.get_place(client_place)
            order_wheight:float = product.weight*ammount
            
            print(self.wharehouses)
        except Exception as e:
            print(e)
        finally:
            return
        pass
    
    def order_products(self, client_place: str, products: dict[Product, int]):
        
        pass
