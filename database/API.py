import sqlite3
import base64
import uuid
import datetime

from classes import Admin, Customer, Product, JSONDefaultResponse
from config import DATABASE_PATH


def generate_id(connection: sqlite3.Connection):
    sql_query_products = '''
        SELECT COUNT (*)
        FROM Products
        WHERE id = ?
    '''

    sql_query_sales = '''
        SELECT COUNT (*)
        FROM Sales
        WHERE id = ?
    '''

    sql_query_supplies = '''
        SELECT COUNT (*)
        FROM Supplies
        WHERE id = ?
    '''

    def generate():
        return str(uuid.uuid4())[-10:].upper()

    cursor = connection.cursor()

    result = 1
    generated_id = ''
    while result:
        generated_id = generate()

        cursor.execute(sql_query_products, (generated_id, ))
        result = int(cursor.fetchone()[0])

        cursor.execute(sql_query_sales, (generated_id, ))
        result += int(cursor.fetchone()[0])

        cursor.execute(sql_query_supplies, (generated_id, ))
        result += int(cursor.fetchone()[0])

    return generated_id

def check_admin_password(admin: Admin):
    sql_query = '''
        SELECT COUNT (*)
        FROM Admins
        WHERE id = ? AND password = ?
    '''

    admin_id        = admin.id
    admin_password  = admin.password

    with sqlite3.connect(DATABASE_PATH) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(sql_query, (admin_id, admin_password))
            result = bool(cursor.fetchone()[0])

            return result
        except Exception as error:
            return False

# Check actual product quantity
def get_actual_quantity(connection: sqlite3.Connection, product: Product):
    sql_query = '''
        SELECT quantity
        FROM Products
        WHERE id = ?
    '''

    product_id = product.id

    cursor = connection.cursor()
    cursor.execute(sql_query, (product_id, ))

    try:
        actual_quantity = int(cursor.fetchone()[0])
        return actual_quantity
    except Exception as error:
        raise Exception(f'No products with ID {product_id}')



def update_quantity(connection: sqlite3.Connection, product: Product):
    sql_query = '''
        UPDATE Products
        SET quantity = quantity - ?
        WHERE id = ?
    '''

    product_quantity = product.quantity
    product_id       = product.id

    if product_quantity > get_actual_quantity(connection, product):
        raise Exception(f'You are trying to buy too much products with ID {product_id}')

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, (product_quantity, product_id))
        connection.commit()
    except Exception:
        raise Exception('Database error: update quantity error')

def insert_customer(connection: sqlite3.Connection, customer: Customer):
    sql_query = '''
        INSERT OR IGNORE INTO Customers
        (email, name)
        VALUES (?, ?)
    '''

    customer_email  = customer.email
    customer_name   = customer.name

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, (customer_email, customer_name))
        connection.commit()

    except Exception:
        raise Exception('Database error: place customer error')

def insert_product(connection: sqlite3.Connection, product: Product):
    sql_query = '''
        INSERT INTO Products
        (id, name, price, quantity, photo_1, photo_2, photo_3)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    product_id          = product.id
    product_name        = product.name
    product_price       = product.price
    product_quantity    = product.quantity


    photo_1 = product.photos.get('photo_1')
    photo_2 = product.photos.get('photo_2')
    photo_3 = product.photos.get('photo_3')

    if photo_1 is not None:
        photo_1 = base64.b64decode(photo_1)
    if photo_2 is not None:
        photo_2 = base64.b64decode(photo_2)
    if photo_3 is not None:
        photo_3 = base64.b64decode(photo_3)

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, (product_id, product_name,
                                   product_price, product_quantity,
                                   photo_1, photo_2, photo_3))
        connection.commit()

    except Exception:
        raise Exception('Database error: place product error')

def insert_supply_operation(connection: sqlite3.Connection, product: Product, admin: Admin):
    sql_query = '''
        INSERT INTO Supplies
        (id, product_id, admin_id, quantity, price, operation_date)
        VALUES (?, ?, ?, ?, ?, ?)
    '''

    supply_id           = 'SP' + generate_id(connection)
    supply_product_id   = product.id
    supply_admin_id     = admin.id
    supply_quantity     = product.quantity
    supply_price        = product.price
    supply_date         = str(datetime.datetime.today())[:10]

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, (supply_id, supply_product_id,
                                   supply_admin_id, supply_quantity,
                                   supply_price, supply_date))
        connection.commit()

    except Exception:
        raise Exception('Database error: place supply operation')

    # connection.commit()

def insert_sale_operation(connection: sqlite3.Connection, product: Product, customer: Customer):
    sql_query = '''
        INSERT INTO Sales
        (id, product_id, quantity, price, user_email, city, address, operation_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''

    sale_id         = 'SL' + generate_id(connection)
    sale_product_id = product.id
    sale_quantity   = product.quantity
    sale_price      = product.price
    sale_user_email = customer.email
    sale_city       = customer.city
    sale_address    = customer.address
    sale_date       = str(datetime.datetime.today())[:10]

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, (sale_id, sale_product_id,
                                   sale_quantity, sale_price,
                                   sale_user_email, sale_city,
                                   sale_address, sale_date))
        connection.commit()

    except Exception:
        raise Exception('Database error: place order operation')

    # connection.commit()


def get_available_products():
    sql_query = '''
        SELECT id, name, price, quantity
        FROM Products
        WHERE quantity != 0
    '''

    with sqlite3.connect(DATABASE_PATH) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(sql_query)

            products = cursor.fetchall()

            result = JSONDefaultResponse()
            for product in products:
                result.data.append({
                    'id':           product[0],
                    'name':         product[1],
                    'price':        product[2],
                    'quantity':     product[3]
                })

            result.error = False
            result.details = 'Executed successfully'

            return result.json()
        except Exception as error:
            result = JSONDefaultResponse(data=[], error=True, details=f'Database error: {error.args[0]}')
            return result.json()

def get_photos(product_id: str):
    sql_query = '''
        SELECT photo_1, photo_2, photo_3
        FROM Products
        WHERE id = ?
    '''

    with sqlite3.connect(DATABASE_PATH) as connection:

        try:
            cursor = connection.cursor()
            cursor.execute(sql_query, (product_id,))
            photos = cursor.fetchone()

            result = []
            for photo in photos:
                if photo is not None:
                    photo = base64.b64encode(photo).decode('utf-8')
                result.append(photo)

            return result
        except Exception as error:
            return None


# Supply function
def supply_product(product: Product, admin: Admin):
    with sqlite3.connect(DATABASE_PATH) as connection:
        if not check_admin_password(admin):
            result = JSONDefaultResponse(
                data=[],
                error=True,
                details='Not authorized'
            )

            return result.json()
        else:
            product.id = 'PR' + generate_id(connection)
            try:
                insert_product(connection, product)
                insert_supply_operation(connection, product, admin)

                response = JSONDefaultResponse(
                    data=[],
                    error=False,
                    details=f'Product {product.id} successfully added'
                )

                return response.json()
            except Exception as error:
                response = JSONDefaultResponse(
                    data=[],
                    error=True,
                    details=error.args[0]
                )

                return response.json()

# Sale function
def sale_product(product: Product, customer: Customer):
    with sqlite3.connect(DATABASE_PATH) as connection:
        try:
            update_quantity(connection, product) # Update quantity and check how much product with such ID we have
            insert_customer(connection, customer) # Insert new customer if he's not already tracked
            insert_sale_operation(connection, product, customer) # Insert sale operation with all data

            response = JSONDefaultResponse(
                data=[],
                error=False,
                details=f'Product {product.id} successfully bought'
            )
            return response.json()

        except Exception as error:
            response = JSONDefaultResponse(
                data=[],
                error=True,
                details=error.args[0]
            )
            return response.json()
