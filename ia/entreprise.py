from ia.map.map import Map
from ia.drivers.driver import Driver
from ia.orders.orders import Order
from ia.orders.product import Product
from ia.algoritm.a_star import a_star_search

class Entreprise:

    def __init__(self):
        self.map = Map()
        self.drivers = Dict()
        self.orders = List()
        self.products = Dict()

    def add_driver(self, driver : Driver):
        self.drivers.add(driver)

    def add_orders(self, order : Order):
        self.orders.add(order)

    def add_product(self, product : Product, place : Place, quantity):
        self.products.add([product,place,quantity])

    def calculate_path(self, order : Order, driver : Driver):
        products = order.products      
        path = a_star_search(self.map, driver.get_place, order.place)
