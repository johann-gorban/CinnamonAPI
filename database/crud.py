
from uuid import uuid4
from pathlib import Path

from sqlalchemy.orm import sessionmaker
from config import DB_PATH, IMAGES_DIR
from sqlalchemy import create_engine
from database.models import Product, Base

engine = create_engine(url=DB_PATH)
Base.metadata.create_all(bind=engine)
session = sessionmaker(bind=engine)()

"""
Additional functions
"""

def _is_product_exists(product_id: str) -> bool:
    product = session.query(Product).filter(Product.id == product_id).first()

    return bool(product)

def _generate_id() -> str:
    new_id = str(uuid4())[:8]
    while _is_product_exists(new_id):
        new_id = str(uuid4())[:8]
    return new_id

"""
Create functions
"""

def get_product_by_id(product_id: str):
    product = session.query(Product).filter(Product.id == product_id).first()

    return product

def get_available_products():
    products = session.query(Product).filter(Product.stock != 0).all()

    return products

def get_all_products():
    products = session.query(Product).all()

    return products

def add_product(name: str,
                stock: int,
                price: int,
                photos: list):

    id = _generate_id()

    photo_urls = []
    for i, photo in enumerate(photos, start=1):
        filename = f'{id}_{i}.jpg'
        filepath = IMAGES_DIR / filename
        if photo is not None:
            with open(filepath, 'ab') as file:
                file.write(photo)
        photo_urls.append(str(filepath))

    product = Product(
        id=id,
        name=name,
        stock=stock,
        price=price,
        photo_1=photo_urls[0] if len(photo_urls) > 0 else None,
        photo_2=photo_urls[1] if len(photo_urls) > 1 else None,
        photo_3=photo_urls[2] if len(photo_urls) > 2 else None,
    )

    session.add(product)
    session.commit()

"""
Delete functions
WARNING: Use only in this file to predict possible leaks
"""

def _delete_product(product_id: str):
    product = get_product_by_id(product_id).dict()
    for i in range(1, 4):
        # deleting all photos
        Path(product[f'photo_{i}']).unlink()

    session.query(Product).filter(Product.id == product_id).delete(synchronize_session=False)
    session.commit()