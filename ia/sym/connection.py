from ia.sym.map.map import Map
from ia.sym.orders.orders import Order
from ia.sym.orders.product import Product
from ia.sym.drivers.driver import Driver

class Connection:

    def __init__(self, map):
        self.map = map
        self.drivers = dict({})
        self.products = dict({})
        self.orders = list()

    def new(self, map):
        Connection.__init__(self,map)

    def add_driver(self, driver):
        id = len(self.drivers) + 1
        driver.set_id = id
        self.drivers |= {id : driver}

    def add_products(self, product : Product, place):
        name = product.get_name()
        if self.map.pickup_points.get(place):
            self.products |= {name : place}
        
    def add_orders(self, order):
        self.orders.append(order)

    def get_all_places_for_order(self, order):
        """
        Dá uma lista de todos os lugares necessários para a order """
        products = order.products
        p_places = list()
        for p in products:
            p_places.append(self.products.get(p))

        return p_places

    