from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipes = relationship("Recipe", back_populates="owner", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="owner", cascade="all, delete-orphan")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), default="")
    servings = Column(Integer, default=1)
    ingredients = Column(JSONB, default=list)
    steps = Column(JSONB, default=list)
    tags = Column(JSONB, default=list)
    favorite = Column(Boolean, default=False)
    planned_to_cook = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    image = Column(String(500), default="")
    prep_time = Column(Integer, default=0)
    cook_time = Column(Integer, default=0)
    difficulty = Column(String(20), default="Media")
    notes = Column(Text, default="")
    rating = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="recipes")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    quantity = Column(Float, default=0)
    unit = Column(String(20), default="")
    low_stock_threshold = Column(Float, default=5)
    low_stock_unit = Column(String(20), default="")

    owner = relationship("User", back_populates="inventory_items")
