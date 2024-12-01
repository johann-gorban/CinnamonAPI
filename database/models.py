"""
File with database classes
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    def dict(self):
        result = {}
        for column in self.__table__.columns:
            result[column.name] = getattr(self, column.name)
        return result

class Product(Base):
    __tablename__ = 'product'

    id      = Column(String, primary_key=True)
    name    = Column(String, nullable=False)
    stock   = Column(Integer, nullable=False)
    price   = Column(Integer, nullable=False)
    photo_1 = Column(String, nullable=False)
    photo_2 = Column(String, nullable=True)
    photo_3 = Column(String, nullable=True)

    supply  = relationship('Supply', back_populates='product')
    sale    = relationship('Sale', back_populates='product')

class Supply(Base):
    __tablename__ = 'supply'

    id          = Column(String, primary_key=True)
    product_id  = Column(String, ForeignKey('product.id'), nullable=False)
    admin_id    = Column(String, ForeignKey('admin.id'), nullable=False)
    quantity    = Column(Integer, nullable=False)
    price       = Column(Integer, nullable=False)

    product = relationship('Product', back_populates='supply')
    admin   = relationship('Admin', back_populates='supply')

class Sale(Base):
    __tablename__ = 'sale'

    id          = Column(String, primary_key=True)
    product_id  = Column(String, ForeignKey('product.id'), nullable=False)
    customer_id = Column(String, ForeignKey('customer.id'), nullable=False)
    quantity    = Column(Integer, nullable=False)
    price       = Column(Integer, nullable=False)

    product     = relationship('Product', back_populates='sale')
    customer    = relationship('Customer', back_populates='product')

class Customer(Base):
    __tablename__ = 'customer'

    id          = Column(String, primary_key=True)
    fullname    = Column(String, nullable=False)
    city        = Column(String, nullable=False)
    address     = Column(String, nullable=False)
    email       = Column(String, nullable=False)
    phone       = Column(String, nullable=False)

    product     = relationship('Sale', back_populates='customer')

class Admin(Base):
    __tablename__ = 'admin'

    id          = Column(String, primary_key=True)
    login       = Column(String, nullable=False)
    password    = Column(String, nullable=False)

    supply = relationship('Supply', back_populates='admin')
