import uuid
from ia.map.place import Place


class Order:

    def __init__(self, time, place : Place):
        self.id = uuid.uuid1()
        self.time = time
        self.place = place
        self.products = dict({})
        self.status = 0
        set.status = [False, False]

    def add_product(self, product : Product):
        if not self.todeliver:
            self.products.add(product)
            self.weight += product.weight

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
        if self.status <= 0 or self.status >= 2:
            self.status = 0
        
        self.status = self.status + 1

        if self.status >= 2:
            self.status = 2
