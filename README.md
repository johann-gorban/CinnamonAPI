# HTTP Requests docs

## Navigation

- [API classes](#classes)
- [GET requests](#get-requests) 
- [POST requests](#post-requests)

## Classes
```
class JSONDefaultResponse:
    data:       List
    error:      bool
    details:    str
```
```
class Customer(BaseModel):
    name:       str
    email:      str
    city:       str
    address:    str
```
```
class Admin(BaseModel):
    id:         str
    password:   str
```
```
class Product(BaseModel):
    id:         str
    name:       str
    quantity:   int
    price:      int
    photos:     Dict[str, str]
```
## GET-Requests

### /products

### /produts/{id}

### /product/{id}/photo_x

## POST-Requests

### /admin-panel/login

### /admin-panel/supply

### /sale

