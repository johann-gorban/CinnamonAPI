from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi import Cookie

from database.API import *
from classes import *

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# GET Requests processing

@app.get('/products')
async def get_catalog():
    """

    :return: list with ids, names, quantities and price of all available products

    In case of errors the function returns 500-error with details

    """
    try:
        response = get_available_products()
        return JSONResponse(response)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {error}")



product_photos_cache: dict = {}

@app.get('/products/{id}')
async def get_product_photos(id: str):
    """

    :param id:  product's unique ID
    :return:    message with caching results

    The function creates cache with photos data for product with given ID
    If product has not enough photos (less than 3) it will cache None-value
    If there is absolutely no photos available it will return 404-error
    In other cases (such as database error) it will return 500-error with details

    """
    try:
        photos = get_photos(id)

        product_photos_cache[id] = {
            'photo_1': photos[0] if len(photos) > 0 else None,
            'photo_2': photos[1] if len(photos) > 1 else None,
            'photo_3': photos[2] if len(photos) > 2 else None
        }

        return {'message': 'Photos cached successfully!'}
    except IndexError:
        raise HTTPException(status_code=404, detail="Not enough photos available")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {error}")

async def get_photo(id: str, photo_key: str):
    """
    :param id:          product's unique ID
    :param photo_key:   photo_1, photo_2 or photo_3 to get photo with such numbers
    :return:            product's photo with photo_key from cache. Could return None if there is no photo

    The function takes data from cache. If there is no cache for the product with given ID or
    there is no photo under such number (i.e. user requests photo_4) the function will return error
    with status code 204

    """
    product_photos = product_photos_cache.get(id)

    if product_photos and product_photos.get(photo_key):
        return Response(content=product_photos[photo_key], media_type="image/jpg")

    return Response(status_code=204)



"""

:return base64-encoded UTF-8 string or None
    
Functions may return errors if there was problem with caching
For details watch comments for get_photos(id, photo_key)

"""

@app.get('/products/{id}/photo_1')
async def get_photo_1(id: str):
    """
    Function to get first photo
    :returns base64 encoded UTF-8 string (encoded JPG)
    """
    return await get_photo(id, 'photo_1')

@app.get('/products/{id}/photo_2')
async def get_photo_2(id: str):
    """
    Function to get second photo
    :returns base64 encoded UTF-8 string (encoded JPG)
    """
    return await get_photo(id, 'photo_2')

@app.get('/products/{id}/photo_3')
async def get_photo_3(id: str):
    """
    Function to get third photo
    :returns base64 encoded UTF-8 string (encoded JPG)
    """
    return await get_photo(id, 'photo_3')






# POST Requests processing

admin_sessions: dict = {}

@app.post('/admin-panel/login')
async def login(admin: Admin, response: Response):
    """
    :param admin:       admin class
    :param response:    response class
    :return:            JSONDefaultResponse

    The function processes login. If admin logged into successfully it will remember it
    setting information in Cookie and return session token
    In case of problem with logging it will return default error 'Incorrect login or password'

    The duration of session is 20 minutes. After that, admin will log out automatically

    """
    if not check_admin_password(admin):
        result = JSONDefaultResponse(data=[], error=True, details='Incorrect login or password')
        return JSONResponse(result.json())

    else:
        session_token = str(uuid.uuid4())[:8] # generate new token
        admin_sessions[session_token] = admin

        response.set_cookie(key='session_token', value=session_token, httponly=True, secure=True, expires=1200)

        result = JSONDefaultResponse(data=[{
            'token': session_token
        }], error=False, details='Successfully authorized')

        return JSONResponse(result.json())

@app.post('/admin-panel/supply')
async def supply(product: Product, session_token = Cookie()):
    """
    :param product:             product data
    :param session_token:       Cookie session token
    :return:                    JSONDefaultResponse

    The function gets new product (name, price, quantity and photos) without ID
    and supplies it into the database.

    In case of problems it will return JSONDefaultResponse with errors

    """
    admin = admin_sessions.get(session_token)
    if admin:
        result = supply_product(product, admin)
        return result
    else:
        result = JSONDefaultResponse(data=[], error=True, details='Not authorized')
        return result.json()

@app.post('/sale')
async def sale(product: Product, customer: Customer):
    """
    :param product:     product data
    :param customer:    customer data
    :return:            JSONDefaultResponse

    The function gets data about product (how much customer wants to buy)
    and customer (address and personal info)

    In case of problems it will return JSONDefaultResponse with errors

    """
    result = sale_product(product, customer)
    return JSONResponse(result)
