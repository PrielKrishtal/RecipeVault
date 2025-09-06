from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


# Use relative imports from within the 'app' package
from .. import schemas, models
from ..db import get_db
from ..security import hash_password, verify_password, create_access_token,get_current_user 


# Create the router with a prefix and tags
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if a user with this email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password and create a new User model instance
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    
    # Save the new user to the database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Return the new user object (without the password)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create the JWT token
    access_token_data = {"sub": str(user.id)}
    access_token = create_access_token(data=access_token_data)
    
    # Return the token
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user's information"""
    return current_user