import pandas as pd
from azure.identity import DefaultAzureCredential
from db_connect import eng
from typing import List, Union
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, DateTime, PrimaryKeyConstraint

Base = declarative_base()

class Brand(Base):
    __tablename__ = 'Brand'
    brand_id = Column(Integer, primary_key=True, nullable=False, index=True)
    brand_name = Column(String)

    laptops = relationship("Laptop", back_populates="Brand")

class User(Base):
    __tablename__ = 'User'
    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    first_name = Column(String)
    last_name = Column(String)
    user_budget = Column(Integer)
    user_major = Column(String)

    wishlist = relationship("Wishlist", back_populates="User")
    major_usages = relationship("MajorUsage", back_populates="User")
    purchase_histories = relationship("PurchaseHistory", back_populates="User")
    reviews = relationship("Review", back_populates="User")

class Laptop(Base):
    __tablename__ = 'Laptop'
    laptop_id = Column(Integer, primary_key=True, nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey(Brand.brand_id), nullable=False)
    laptop_model = Column(String)
    processor_brand = Column(String)
    processor_name = Column(String)
    ram_gb = Column(Integer)
    ssd_gb = Column(Integer)
    hdd_gb = Column(Integer)
    operating_system = Column(String)
    laptop_weight = Column(Integer)
    display_size = Column(Float)
    touchscreen = Column(String)
    laptop_price = Column(Integer)

    brand = relationship("Brand", back_populates="laptops")
    wishlist_items = relationship("WishlistItem", back_populates="laptop")
    purchased_items = relationship("PurchasedItem", back_populates="laptop")
    reviews = relationship("Review", back_populates="laptop")

class Usage(Base):
    __tablename__ = 'Usage'
    usage_id = Column(Integer, primary_key=True, nullable=False, index=True)
    usage_type = Column(String)

    major_usages = relationship("MajorUsage", back_populates="usage")

class MajorUsage(Base):
    __tablename__ = 'Major_Usage'
    usage_id = Column(Integer, ForeignKey(Usage.usage_id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.user_id), nullable=False)
    major_note = Column(String)
    __table_args__ = (
        PrimaryKeyConstraint('usage_id', 'user_id', name='PK_Major_Usage'),
    )

    usage = relationship("Usaage", back_populates="major_usages")
    user = relationship("User", back_populates="major_usages")

class PurchaseHistory(Base): 
    __tablename__ = 'Purchase_History'
    purchase_history_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey(User.user_id), nullable=False)
    date_created = Column(DateTime, nullable=False)
    time_created = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="purchase_histories")
    purchased_items = relationship("PurchasedItem", back_populates="purchase_history")

class PurchasedItem(Base):
    __tablename__ = 'Purchased_Item'
    purchase_history_id = Column(Integer, ForeignKey(PurchaseHistory.purchase_history_id), nullable=False)
    laptop_id = Column(Integer, ForeignKey(Laptop.laptop_id), nullable=False)
    date_purchased = Column(DateTime, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('purchase_history_id', 'laptop_id', name='PK_Purchased_Item'),
    )
    
    purchase_history = relationship("PurchaseHistory", back_populates="purchased_items")
    laptop = relationship("Laptop", back_populates="purchased_items")
    reviews = relationship("Review", back_populates="purchased_item")

class Review(Base):
    __tablename__ = 'Review'
    review_id = Column(Integer, primary_key=True, nullable=False, index=True)
    purchase_history_id = Column(Integer, ForeignKey(PurchasedItem.purchase_history_id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.user_id), nullable=False)
    laptop_id = Column(Integer, ForeignKey(PurchasedItem.laptop_id), nullable=False)
    review_rating = Column(Float, nullable=False)
    review_comment = Column(String)

    purchased_item = relationship("PurchasedItem", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    laptop = relationship("Laptop", back_populates="reviews")

class Wishlist(Base):
    __tablename__ = 'Wishlist'
    wishlist_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey(User.user_id), nullable=False)
    date_created = Column(DateTime, nullable=False)
    time_created = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="wishlist")
    laptop = relationship("Laptop", back_populates="wishlist_items")

class WishlistItem(Base):
    __tablename__ = "Wishlist_Item"
    wishlist_id = Column(Integer, ForeignKey(Wishlist.wishlist_id), nullable=False)
    laptop_id = Column(Integer, ForeignKey(Laptop.laptop_id), nullable=False)
    date_added = Column(DateTime, nullable=False)
    time_added = Column(DateTime, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('wishlist_id', 'laptop_id', name='PK_Wishlist_Item'),
    )
