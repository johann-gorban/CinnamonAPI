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

Product class stores default information about product.
Photos dictionary will store up to 3 photos into database
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
Returns JSONDefaultResponse with list of product data; id, name, quantity and price

### /produts/{id}
Caches product photos

### /product/{id}/photo_x
Params:
    id - string. Product ID
    x  - photo number. 1, 2 or 3
Returns:
    Base64 encoded JPG image

To decode image use base64 decoding

## POST-Requests

### /admin-panel/login
Params:
    admin     - Admin class;
    response  - Response (???)
Returns:
    JSONDefaultReponse

Check whether admin with given password and login exists. Set Cookie (expires in 20 minutes) if exists

### /admin-panel/supply
Params: 
    product - Product class. All data except ID (it creates automatically)
Returns:
    JSONDefaultResponse with result

Product should have name, quantity, price and encoded into base64 photos
User should have admin Cookie to supply product

### /sale
Params:
    product     - Product class. All data except photos and name
    customer    - customer class
Returns:
    JSONDefaultReponse
