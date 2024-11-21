import sqlite3
import base64
import uuid
import datetime

from classes import Admin, Customer, Product, JSONDefaultResponse
from config import DATABASE_PATH


def _generate_id(connection: sqlite3.Connection):
    """
    :param connection:  SQLite3 connection with database
    :return:            unique ID
    """
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

def check_admin_password(admin: Admin) -> bool:
    """
    :param admin:   admin data
    :return:        True if admin exists and False otherwise

    """
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
            raise Exception('Database error: failed to check admin')

def _get_actual_quantity(connection: sqlite3.Connection, product: Product):

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



def _update_quantity(connection: sqlite3.Connection, product: Product):
    """
    :param connection:  SQLite3 connection with database
    :param product:     product data
    :return:            Nothing

    The function updates product's quantity with given ID


    """
    sql_query = '''
        UPDATE Products
        SET quantity = quantity - ?
        WHERE id = ?
    '''

    product_quantity = product.quantity if product.quantity > 0 else 0
    product_id       = product.id

    if product_quantity > _get_actual_quantity(connection, product):
        raise Exception(f'You are trying to buy too much products with ID {product_id}')

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query, (product_quantity, product_id))
        connection.commit()
    except Exception:
        raise Exception('Database error: failed to update product info')

def _insert_customer(connection: sqlite3.Connection, customer: Customer):
    """
    :param connection:      SQLite3 connection with database
    :param customer:        customer data (email and name)
    :return:                Nothing

    The function inserts new customer if he doesn't exist in database yet

    In case of problems it will raise an exception

    """
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

def _insert_product(connection: sqlite3.Connection, product: Product):
    """
    :param connection:      SQLite3 connection with database
    :param product:         product data
    :return:                Nothing

    The function inserts new product into database

    In case of problems the function will raise an exception

    """
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

def _insert_supply_operation(connection: sqlite3.Connection, product: Product, admin: Admin):
    """
    :param connection:  SQLite3 connection with database
    :param product:     product data
    :param admin:       admin data
    :return:            Nothing

    The function inserts new supply operation with given admin and product info

    In case of problems it will raise an exception

    """
    sql_query = '''
        INSERT INTO Supplies
        (id, product_id, admin_id, quantity, price, operation_date)
        VALUES (?, ?, ?, ?, ?, ?)
    '''

    supply_id           = 'SP' + _generate_id(connection)
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

def _insert_sale_operation(connection: sqlite3.Connection, product: Product, customer: Customer):
    """
    :param connection:  SQLite3 connection with database
    :param product:     product data
    :param customer:    customer data (address and personal info)
    :return:            Nothing

    The function inserts sale operation for given customer and product info

    In case of problems it will raise an exception

    """
    sql_query = '''
        INSERT INTO Sales
        (id, product_id, quantity, price, user_email, city, address, operation_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''

    sale_id         = 'SL' + _generate_id(connection)
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
    """
    :return:    JSONDefaultResponse

    The function returns list of available products

    In case of problems it will raise an exception
    """
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
    """
    :param product_id:  product ID
    :return:            list of base64 UTF-8 strings

    The function gets all available photos of product from database in base64 encoding

    In case of problems it will raise an exception
    """
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
            raise Exception('Database error: failed to get images')


def supply_product(product: Product, admin: Admin):
    """
    :param product:     product to supply data
    :param admin:       admin supplier data
    :return:            JSONDefaultResponse

    The function gets new product (name, price, quantity and photos) without ID
    and supplies it into the database.

    In case of problems it will return JSONDefaultResponse with errors

    """
    with sqlite3.connect(DATABASE_PATH) as connection:
        try:
            if not check_admin_password(admin):
                return JSONDefaultResponse(
                    data=[],
                    error=True,
                    details='Not authorized'
                ).json()

            product.id = 'PR' + _generate_id(connection)

            with connection:
                _insert_product(connection, product)
                _insert_supply_operation(connection, product, admin)

            return JSONDefaultResponse(
                data={'product_id': product.id},
                error=False,
                details=f'Product {product.id} successfully added'
            ).json()

        except sqlite3.IntegrityError as integrity_error:

            return JSONDefaultResponse(
                data=[],
                error=True,
                details=f"Database integrity error: {str(integrity_error)}"
            ).json()

        except Exception as error:

            return JSONDefaultResponse(
                data=[],
                error=True,
                details=f"Unexpected error: {str(error)}"
            ).json()



def sale_product(product: Product, customer: Customer):
    """
    :param product:        product to sale data
    :param customer:       customer data (address and contact information)
    :return:                JSONDefaultResponse

    The function gets data about product (how much customer wants to buy)
    and customer (address and personal info)

    In case of problems it will return JSONDefaultResponse with errors

    """
    with sqlite3.connect(DATABASE_PATH) as connection:
        try:
            # Use a transaction to ensure atomicity of operations
            with connection:
                _update_quantity(connection, product)  # Update product quantity
                _insert_customer(connection, customer)  # Insert customer if not already tracked
                _insert_sale_operation(connection, product, customer)  # Insert sale operation

            # Successful response with product and customer details
            return JSONDefaultResponse(
                data=[{
                    'product_id': product.id,
                    'customer_name': customer.name  # Or other relevant details
                }],
                error=False,
                details=f'Product {product.id} successfully bought by {customer.name}'
            ).json()

        except sqlite3.IntegrityError as integrity_error:
            # Handle specific database issues, such as quantity constraints
            return JSONDefaultResponse(
                data=[],
                error=True,
                details=f"Database integrity error: {str(integrity_error)}"
            ).json()

        except sqlite3.OperationalError as operational_error:
            # Handle operational errors, such as failed database operations
            return JSONDefaultResponse(
                data=[],
                error=True,
                details=f"Operational error: {str(operational_error)}"
            ).json()

        except Exception as error:
            # General exception handler for unexpected issues
            return JSONDefaultResponse(
                data=[],
                error=True,
                details=f"Unexpected error: {str(error)}"
            ).json()
