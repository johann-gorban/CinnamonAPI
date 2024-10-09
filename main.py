from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi import Cookie

import uuid
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
    response = get_available_products()
    return JSONResponse(response)

@app.get('/products/{id}')
async def get_product(id: str):
    response = get_product_info(id)
    return JSONResponse(response)


# POST Requests processing

admin_sessions: dict = {}

@app.post('/admin-panel/login')
async def login(admin: Admin, response: Response):
    print(check_admin_password(admin))
    if not check_admin_password(admin):
        result = JSONDefaultResponse(data=[], error=True, details='Incorrect login or password')
        return JSONResponse(result.json())
    else:
        session_token = str(uuid.uuid4())[:8] # generate new token
        admin_sessions[session_token] = admin
        response.set_cookie(key='session_token', value=session_token, httponly=True, secure=True)

        result = JSONDefaultResponse(data=[{
            'token': session_token
        }], error=False, details='Successfully authorized')

        return JSONResponse(result.json())

@app.post('/admin-panel/supply')
async def supply(product: Product, session_token = Cookie()):
    admin = admin_sessions.get(session_token)
    if admin:
        result = supply_product(product, admin)
        return JSONResponse(result)
    else:
        result = JSONDefaultResponse(data=[], error=True, details='Not authorized')
        return JSONResponse(result.json())

@app.post('/sale')
async def sale(product: Product, customer: Customer):
    result = sale_product(product, customer)
    return JSONResponse(result)
