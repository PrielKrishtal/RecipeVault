from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

# Use relative imports from within the 'app' package
from .. import schemas, models
from ..db import get_db
from ..security import hash_password, verify_password, create_access_token,get_current_user
from sqlalchemy.orm import joinedload

# Create the router with a prefix and tags
router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)

@router.post("/", response_model=schemas.RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    ingredient_data = recipe.ingredients
    recipe_data = recipe.model_dump(exclude={"ingredients"})

    db_recipe = models.Recipe(**recipe_data, owner_id=current_user.id)
    db.add(db_recipe)
    db.flush()  # Get ID
    
    for ingredient_item in ingredient_data:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_item.name).first()
        if not ingredient:
            ingredient = models.Ingredient(name=ingredient_item.name)
            db.add(ingredient)
            db.flush()

        # Create the Association Object instance with the extra data
        association = models.RecipeIngredient(
            recipe=db_recipe, 
            ingredient=ingredient, 
            amount_text=ingredient_item.amount_text
        )
        db.add(association)

    db.commit()
    db.refresh(db_recipe)
    
    # Build response with ingredients - NO IMAGE
    recipe_ingredients = db.query(models.RecipeIngredient).join(
        models.Ingredient
    ).filter(
        models.RecipeIngredient.recipe_id == db_recipe.id
    ).all()
    
    ingredients = []
    for recipe_ingredient in recipe_ingredients:
        ingredients.append({
            "name": recipe_ingredient.ingredient.name,
            "amount_text": recipe_ingredient.amount_text
        })
    
    return {
        "id": db_recipe.id,
        "title": db_recipe.title,
        "description": db_recipe.description,
        "cook_time_minutes": db_recipe.cook_time_minutes,
        "owner_id": db_recipe.owner_id,
        "ingredients": ingredients
    }

@router.get("/", response_model=List[schemas.RecipeRead])
def get_all_recipes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get all recipes for the current user"""
    recipes = db.query(models.Recipe).filter(models.Recipe.owner_id == current_user.id).all()
    
    result = []
    for recipe in recipes:
        # Get ingredients for each recipe
        recipe_ingredients = db.query(models.RecipeIngredient).join(
            models.Ingredient
        ).filter(
            models.RecipeIngredient.recipe_id == recipe.id
        ).all()
        
        ingredients = []
        for recipe_ingredient in recipe_ingredients:
            ingredients.append({
                "name": recipe_ingredient.ingredient.name,
                "amount_text": recipe_ingredient.amount_text
            })
        
        recipe_dict = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "cook_time_minutes": recipe.cook_time_minutes,
            "owner_id": recipe.owner_id,
            "ingredients": ingredients
        }
        result.append(recipe_dict)
    
    return result

@router.get("/{recipe_id}", response_model=schemas.RecipeRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get a single recipe by ID with ingredients"""
    recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.owner_id == current_user.id
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Get the ingredients for this recipe from the recipe_ingredients table
    recipe_ingredients = db.query(models.RecipeIngredient).join(
        models.Ingredient
    ).filter(
        models.RecipeIngredient.recipe_id == recipe_id
    ).all()
    
    # Build the ingredients list
    ingredients = []
    for recipe_ingredient in recipe_ingredients:
        ingredient_data = {
            "name": recipe_ingredient.ingredient.name,
            "amount_text": recipe_ingredient.amount_text
        }
        ingredients.append(ingredient_data)
    
    # Create the response manually to include ingredients - NO IMAGE
    recipe_dict = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "cook_time_minutes": recipe.cook_time_minutes,
        "owner_id": recipe.owner_id,
        "ingredients": ingredients
    }
    
    return recipe_dict

@router.get("/search/", response_model=List[schemas.RecipeRead])
def search_recipes(q: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Search recipes by title or description"""
    search_term = f"%{q}%"
    
    recipes = db.query(models.Recipe).filter(
        models.Recipe.owner_id == current_user.id,
        (models.Recipe.title.ilike(search_term) | 
         models.Recipe.description.ilike(search_term))
    ).all()
    
    result = []
    for recipe in recipes:
        # Get ingredients for each recipe
        recipe_ingredients = db.query(models.RecipeIngredient).join(
            models.Ingredient
        ).filter(
            models.RecipeIngredient.recipe_id == recipe.id
        ).all()
        
        ingredients = []
        for recipe_ingredient in recipe_ingredients:
            ingredients.append({
                "name": recipe_ingredient.ingredient.name,
                "amount_text": recipe_ingredient.amount_text
            })
        
        recipe_dict = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "cook_time_minutes": recipe.cook_time_minutes,
            "owner_id": recipe.owner_id,
            "ingredients": ingredients
        }
        result.append(recipe_dict)
    
    return result

@router.patch("/{recipe_id}", response_model=schemas.RecipeRead)
def update_recipe(recipe_id: int, updated_recipe: schemas.RecipeUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == recipe_id)
    recipe = recipe_query.first()

    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe with id {recipe_id} not found")
    
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    # Use model_dump with exclude_unset=True for PATCH-like behavior
    update_data = updated_recipe.model_dump(exclude_unset=True)
    
    # Corrected line: call update() on the query object, not the instance
    recipe_query.update(update_data)
    
    db.commit()
    
    # We need to get the refreshed object to return it
    return recipe_query.first()

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # First, find the recipe and verify ownership
    recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.owner_id == current_user.id
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Delete all ingredients for this recipe FIRST
    db.query(models.RecipeIngredient).filter(
        models.RecipeIngredient.recipe_id == recipe_id
    ).delete()
    
    # Then delete the recipe itself
    db.delete(recipe)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)