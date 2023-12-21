import uuid
from ia.map.place import Place

class Order:

    def __init__(self, time, place : Place):
        self.id = uuid.uuid1()
        self.time = time
        self.place = place
        self.products = dict({})
        self.rating = 0
        self.weight = 0
        set.status = [False, False]

    def add_product(self, product : Product):
        if not self.todeliver:
            self.products.add(product)
            self.weight += product.weight

    def set_rating(self, rating):
        if not self.delivered:
            self.rating = rating

    def ask_delivery(self):
        self.done = True

    def deliver(self):
        self.delivered = True

            

        