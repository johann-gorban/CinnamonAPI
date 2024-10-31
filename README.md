# HTTP Requests docs
Current version: dev v2.5

## Navigation

- [API classes](#classes)
- [GET requests](#get-requests) 
- [POST requests](#post-requests)

## Classes
### JSONDefaultReponse
Represents the standard structure for all responses.
```
class JSONDefaultResponse:
    data:       List  # Response data
    error:      bool  # Indicates if an error occurred
    details:    str   # Additional details or error message
```
### Customer
Represents customer information.
```
class Customer(BaseModel):
    name:       str    # Customer's name
    email:      str    # Customer's email
    city:       str    # City where the customer resides
    address:    str    # Customer's address
```
### Admin
Used for admin authentication.
```
class Admin(BaseModel):
    id:         str    # Admin's unique identifier
    password:   str    # Admin's password
```

### Product
Stores information about a product. The photos field can contain up to 3 base64 encoded image.
```
class Product(BaseModel):
    id:         str             # Product ID
    name:       str             # Product name
    quantity:   int             # Available stock quantity
    price:      int             # Product price
    photos:     Dict[str, str]  # Dictionary storing up to 3 base64-encoded photos
```
## GET-Requests

### /products
Retrieves a list of all products.

Response:
- JSONDefaultResponse: contains a list of products (id, name, quantity, price)

### /produts/{id}
Caches product photos.

Response:
- JSONDefaultResponse: empty response with error status (True of False)

### /product/{id}/photo_x
Retrieves a specific photo of the product by its index (x).

Params:
* id: Product ID (string)
* x:  Photo number (1, 2 or 3)

Reponse:
- Base64-encoded JPG image

Note:
- To display image, decode the base64 string 

## POST-Requests

### /admin-panel/login
Authenticates an admin and creates a session.

Params:
- admin:     Object of the Admin class containing id and password

Reponse:
- JSONDefaultReponse: Indicates success or failure

Behavior:
- If the credentials are valid, a session cookie is set (expires in 20 minutes)

### /admin-panel/supply
Supplies a new product to the inventory.

Params: 
- product: Object of the Product class, excluding id (generated automatically)
  
Reponse:
- JSONDefaultResponse: Contains the result of the operation

Notes:
- Product information must include name, quantity, price, and up to 3 base64-encoded photos;
- Admin must have a valid session cookie to perform this action

### /sale
Processes a sale for a customer.

Params:
- product: Object of the Product class, excluding photos and name
- customer: Object of the Customer class containing customer details

Response:
- JSONDefaultReponse: contains the result of the operation
