from pydantic import BaseModel
from typing import Dict, List


# Product class
class Product(BaseModel):
    id:         str
    name:       str
    quantity:   int
    price:      int
    photos:     Dict[str, str]

    def __init__(self,
                 id: int = None,
                 name:str = None,
                 quantity: int = None,
                 price: int = None,
                 photos: Dict[str, str] = None):

        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.photos = photos

# Admin class
class Admin(BaseModel):
    id: str
    password: str

# Customer class
class Customer(BaseModel):
    name:       str
    email:      str
    city:       str
    address:    str

# Interface class for supply and sale classes
class Operation(BaseModel):
    id:         str
    product:    Product

# Supply operation class
class Supply(Operation):
    admin: Admin

# Sale operation class
class Sale(Operation):
    customer: Customer


class JSONDefaultResponse:
    data:       List
    error:      bool
    details:    str

    def __init__(self, data: List = None, error: bool = None, details: str = None):
        self.data = data
        self.error = error
        self.details = details

        if data is None:
            self.data = []
        if error is None:
            self.error = True
        if details is None:
            self.details = 'JSON Response is not initialized'


    def json(self):
        return {
            'data':     self.data,
            'error':    self.error,
            'details':  self.details
        }