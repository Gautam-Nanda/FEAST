from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    # user_id, roll_no, name, email, phone_number, password, can make reviews and orders
    user_id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)

    # one to many relationship with orders
    orders = relationship("Order", back_populates="customer")

    # one to many relationship with reviews
    reviews = relationship("Review", back_populates="reviewer")

class Shop(Base):
    __tablename__ = "shops"

    # shop_id, name, address, description, contact, receives orders, has reviews
    shop_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    description = Column(String)
    contact = Column(String, index=True)

    # one to many relationship with orders
    orders = relationship("Order", back_populates="shop")

    # one to many relationship with reviews
    reviews = relationship("Review", back_populates="reviewed_shop")

class Order(Base):
    __tablename__ = "orders"

    # id, user_id, shop_id, created_at, status
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    shop_id = Column(Integer, ForeignKey("shops.shop_id"))
    created_at = Column(String)
    status = Column(String)

    # many to one relationship with users
    customer = relationship("User", back_populates="orders")

    # many to one relationship with shops
    shop = relationship("Shop", back_populates="orders")

class Review(Base):
    __tablename__ = "reviews"

    # id, user_id, shop_id, created_at, rating, comment
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    shop_id = Column(Integer, ForeignKey("shops.shop_id"))
    created_at = Column(String)
    rating = Column(Integer)
    comment = Column(String)

    # many to one relationship with users
    reviewer = relationship("User", back_populates="reviews")

    # many to one relationship with shops
    reviewed_shop = relationship("Shop", back_populates="reviews")



