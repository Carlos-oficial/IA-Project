class Warehouse(Place):

    def __init__(self):
        super(self)
        self.storage: Dict[str, int] = {}

    def get_products(self):
        return self.storage

    #Gets the product and the quantity in the warehouse
    def get_product(self, product):
        return self.storage.get(product)