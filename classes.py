from pydantic import BaseModel
from typing import Dict, List


# Product class
class Product(BaseModel):
    id:         str
    name:       str
    quantity:   int
    price:      int
    photos:     Dict[str, str]

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