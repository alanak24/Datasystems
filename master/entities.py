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
    Brand_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    Brand_Name = Column(String)

    laptops = relationship("Laptop", back_populates="brand")

class User(Base):
    __tablename__ = 'User'
    User_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    First_Name = Column(String)
    Last_Name = Column(String)
    User_Budget = Column(Integer)
    User_Major = Column(String)

    wishlist = relationship("Wishlist", back_populates="User")
    major_usages = relationship("MajorUsage", back_populates="User")
    purchase_histories = relationship("PurchaseHistory", back_populates="User")
    reviews = relationship("Review", back_populates="User")

class Laptop(Base):
    __tablename__ = 'Laptop'
    Laptop_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    Brand_ID = Column(Integer, ForeignKey(Brand.Brand_ID), nullable=False)
    Laptop_Model = Column(String)
    Processor_Brand = Column(String)
    Processor_Name = Column(String)
    RAM_GB = Column(Integer)
    SSD_GB = Column(Integer)
    HDD_GB = Column(Integer)
    Operating_System = Column(String)
    Laptop_Weight = Column(Integer)
    Display_Size = Column(Float)
    Touchscreen = Column(String)
    Laptop_Price = Column(Integer)

    brand = relationship("Brand", back_populates="laptops")
    wishlist_items = relationship("WishlistItem", back_populates="laptop")
    purchased_items = relationship("PurchasedItem", back_populates="laptop")
    reviews = relationship("Review", back_populates="laptop")

class Usage(Base):
    __tablename__ = 'Usage'
    Usage_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    Usage_Type = Column(String)

    major_usages = relationship("MajorUsage", back_populates="usage")

class MajorUsage(Base):
    __tablename__ = 'Major_Usage'
    Usage_ID = Column(Integer, ForeignKey(Usage.Usage_ID), nullable=False)
    User_ID = Column(Integer, ForeignKey(User.User_ID), nullable=False)
    Major_Note = Column(String)
    __table_args__ = (
        PrimaryKeyConstraint('Usage_ID', 'User_ID', name='PK_Major_Usage'),
    )

    usage = relationship("Usage", back_populates="major_usages")
    user = relationship("User", back_populates="major_usages")

class PurchaseHistory(Base): 
    __tablename__ = 'Purchase_History'
    Purchase_History_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    User_ID = Column(Integer, ForeignKey(User.User_ID), nullable=False)
    Date_Created = Column(DateTime, nullable=False)
    Time_Created = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="purchase_histories")
    purchased_items = relationship("PurchasedItem", back_populates="purchase_history")

class PurchasedItem(Base):
    __tablename__ = 'Purchased_Item'
    Purchase_History_ID = Column(Integer, ForeignKey(PurchaseHistory.Purchase_History_ID), nullable=False)
    Laptop_ID = Column(Integer, ForeignKey(Laptop.Laptop_ID), nullable=False)
    Date_Purchased = Column(DateTime, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('Purchase_History_ID', 'Laptop_ID', name='PK_Purchased_Item'),
    )
    
    purchase_history = relationship("PurchaseHistory", back_populates="purchased_items")
    laptop = relationship("Laptop", back_populates="purchased_items")
    reviews = relationship("Review", back_populates="purchased_item")

class Review(Base):
    __tablename__ = 'Review'
    Review_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    Purchase_History_ID = Column(Integer, ForeignKey(PurchasedItem.Purchase_History_ID), nullable=False)
    User_ID = Column(Integer, ForeignKey(User.User_ID), nullable=False)
    Laptop_ID = Column(Integer, ForeignKey(PurchasedItem.Laptop_ID), nullable=False)
    Review_Rating = Column(Float, nullable=False)
    Review_Comment = Column(String)

    purchased_item = relationship("PurchasedItem", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    laptop = relationship("Laptop", back_populates="reviews")

class Wishlist(Base):
    __tablename__ = 'Wishlist'
    Wishlist_ID = Column(Integer, primary_key=True, nullable=False, index=True)
    User_ID = Column(Integer, ForeignKey(User.User_ID), nullable=False)
    Date_Created = Column(DateTime, nullable=False)
    Time_Created = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="wishlist")
    laptop = relationship("Laptop", back_populates="wishlist_items")

class WishlistItem(Base):
    __tablename__ = "Wishlist_Item"
    Wishlist_ID = Column(Integer, ForeignKey(Wishlist.Wishlist_ID), nullable=False)
    Laptop_ID = Column(Integer, ForeignKey(Laptop.Laptop_ID), nullable=False)
    Date_Added = Column(DateTime, nullable=False)
    Time_Added = Column(DateTime, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('Wishlist_ID', 'Laptop_ID', name='PK_Wishlist_Item'),
    )