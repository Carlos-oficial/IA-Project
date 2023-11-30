import uuid
from ia.map.place import Place

class Order:

    def __init__(self, time, place):
        self.id = uuid.uuid1()
        self.time = time
        self.place = place
        self.products = dict({})
        self.rating = 0
        self.weight = 0

    def add_product(self, product):
        self.products.add(product)
        self.weight += product.weight

    def set_rating(self, rating):
        self.rating = rating

            

        