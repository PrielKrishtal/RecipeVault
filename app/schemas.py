from pydantic import BaseModel, Field,  field_validator
from typing import Optional

# --- Schemas for Authentication ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Schemas for Users ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

    @field_validator('email')
    def email_must_be_gmail(cls, v):
        if not v.endswith('@gmail.com'):
            raise ValueError('must be a Gmail address')
        return v

class UserRead(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Schemas for Recipes ---

# This is the data we expect from the user for one ingredient
class RecipeIngredientCreate(BaseModel):
    name: str
    amount_text: str

# This is how we will display one ingredient in a recipe response
class RecipeIngredientRead(BaseModel):
    name: str
    amount_text: str
    
    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: Optional[str] = None
    cook_time_minutes: int = Field(ge=0)

class RecipeCreate(RecipeBase):
    ingredients: list[RecipeIngredientCreate] = []

class RecipeUpdate(RecipeBase):
    title: Optional[str] = Field(min_length=3, max_length=80, default=None)
    description: Optional[str] = None
    cook_time_minutes: Optional[int] = Field(ge=0, default=None)

class RecipeRead(RecipeBase):
    id: int
    owner_id: int
    ingredients: list[RecipeIngredientRead] = []

    class Config:
        from_attributes = True


