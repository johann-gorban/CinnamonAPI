from pathlib import Path

from fastapi import FastAPI, UploadFile, Form
from .crud import add_product, get_available_products, get_product_by_id

from fastapi.responses import FileResponse
from fastapi.responses import Response

app = FastAPI()

@app.post("add-product")
async def add_new_product(
    name: str,
    quantity: int,
    price: int,
    photo_1: UploadFile,
    photo_2: UploadFile = None,
    photo_3: UploadFile = None
):
    photo_files = [
        photo_1.file.read(),
        photo_2.file.read(),
        photo_3.file.read()
    ]

    add_product(name, quantity, price, photo_files)

    return {"message": "Product added successfully"}


@app.get('/get-available')
async def get_available():
    products = get_available_products()

    result = []
    for product in products:
        result.append(product.dict())

    return result

@app.get('/get-full-info')
async def get_full_info(product_id: str):
    return get_product_by_id(product_id).dict()

@app.get('/media/images/{id}_{photo_index}.jpg')
async def get_photo(id: str, photo_index: str):
    path = Path(f'media/images/{id}_{photo_index}.jpg')
    with open(path, 'rb') as file:
        return Response(content=file.read(),
                        media_type='image/jpg')
