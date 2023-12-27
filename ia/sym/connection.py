from ia.sym.drivers.driver import Driver
from ia.sym.map.map import Map
from ia.sym.orders.products import *


class Connection:
    def __init__(self, map):
        self.map = map
        self.drivers = dict({})
        self.orders = dict({})  # Mapeia os produtos para o lugar onde estão
        self.products = list()

    def new(self, map):
        Connection.__init__(self, map)

    def add_driver(self, driver):
        id = len(self.drivers) + 1
        driver.set_id = id
        self.drivers |= {id: driver}

    def add_products(self, product: Product, place):
        name = product.get_name()
        if self.map.pickup_points.get(place):
            self.products = {name: place}

    def add_products(self, order):
        self.products.append(order)

    def get_all_places_for_order(self, order):
        """
        Dá uma lista de todos os lugares necessários para a order"""
        products = order.products
        p_places = order.to_visit_places
        for p in products:
            place = self.products(get(p))
            p_places.add_places_to_visit(place)

    def run_pre_algorithm(self, driver, order):
        d_place = driver.place
        last_place = order.place
        get_all_places_for_order(order)
        all_nodes = Set.copy(order.to_visit_places).add(last_place)

        return RestrictedTourSearch.run(
            d_place, all_nodes, {last_place: order.to_visit_places}
        )

    def run_driver_algorithm(self, driver, order):
        pre_algorithm = self.run_pre_algorithm(driver, order)

        ### Algoritmo de exploração do driver aqui (tenho que ver como fazer)
