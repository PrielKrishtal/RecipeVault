from .db import Base
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text, CheckConstraint, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

# TODO: FIX RECIPE DELETE FUNCTIONALITY - FOREIGN KEY CONSTRAINT ERROR

# file: app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, CheckConstraint
from sqlalchemy.orm import relationship
from .db import Base

# This is our new Association Object Model
class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    recipe_id = Column(ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = Column(ForeignKey('ingredients.id'), primary_key=True)
    amount_text = Column(String, nullable=False)
    
    # Relationships back to Recipe and Ingredient
    recipe = relationship("Recipe", back_populates="ingredient_associations")
    ingredient = relationship("Ingredient", back_populates="recipe_associations")

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    cook_time_minutes = Column(Integer, CheckConstraint('cook_time_minutes >= 0'), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="recipes")
    
    # This relationship now points to the Association Object
    ingredient_associations = relationship("RecipeIngredient", back_populates="recipe")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    # This relationship now points to the Association Object
    recipe_associations = relationship("RecipeIngredient", back_populates="ingredient")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    recipes = relationship("Recipe", back_populates="owner")