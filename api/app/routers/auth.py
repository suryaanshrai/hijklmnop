from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.schemas import User
from app.dependencies.database import db_dependency
from app.dependencies.auth import auth_dependency
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user_models import CreateUser, ResponseUser, ResponseUsername, UpdateUser, TokenResponse, LoginUser
from zxcvbn import zxcvbn
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/")
async def get_user(user: auth_dependency, db: db_dependency):
    """
    ## Returns the username of the authenticated user.

    ### Args: 
    - None

    ### Raises:
    - **HTTPException  401**: If the user is not authenticated

    ### Returns:
    - **dict[str, str]**: A dictionary containing the username of the authenticated user
    """
    return {"username": user["username"]}



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: CreateUser, db: db_dependency) -> ResponseUser:
    """
    ## Creates a new user in the database.

    ### Args:
    - **username**: The username for the new user
    - **password1**: The password for the new user
    - **password2**: Confirmation for the password 

    ### Raises:
    - **HTTPException 401**: If the user already exists, passwords do not match, or password is weak

    ### Returns:
    - **dict[str, str]**: A dictionary containing the username and access token of the newly created user
    """
    try:
        query = db.query(User).filter(User.username == user.username)
        if query.first():
            raise HTTPException(status_code=400, detail="User already exists")
        
        if user.password1 != user.password2:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        pswd_check = zxcvbn(user.password1, user_inputs=[user.username])
        if pswd_check['score'] < 3 or pswd_check["feedback"]["warning"] or pswd_check["feedback"]["suggestions"]:
            raise HTTPException(status_code=400, detail=f"Weak password:{pswd_check["feedback"]["warning"]} {" ".join(pswd_check["feedback"]["suggestions"])}")
        
        new_user = User(username=user.username, password=bcrypt_context.hash(user.password1))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        access_token = create_access_token(new_user.username, new_user.id)
        
        return {"username" : new_user.username, "access_token" : access_token}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/token", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """
    ## Returns an access token for the authenticated user.

    ### Args:
    - **username**: The username for the user
    - **password**: The password for the user

    ### Raises:
    - **HTTPException 401**: If the user is not authenticated

    ### Returns:
    - **dict[str, str]**: A dictionary containing the access token and token type
    """
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        access_token = create_access_token(user.username, user.id)
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
    
@router.put("/update", response_model=ResponseUsername)
async def update_user(new_user: UpdateUser, user: auth_dependency, db: db_dependency):
    """
    ## Update the user whose token is provided

    ### Args:
    - **username**: The new username for the user
    - **password1**: The new password for the user
    - **password2**: Confirmation for the password 

    ### Raises:
    - **HTTPException 401**: If the user is not authenticated
    - **HTTPException 400**: If the passwords do not match or the password is weak

    ### Returns:
    - **dict[str, str]**: A dictionary containing the new username of the user
    """
    try:
        if new_user.password1 != new_user.password2:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        pswd_check = zxcvbn(new_user.password1, user_inputs=[new_user.username])
        if pswd_check['score'] < 3 or pswd_check["feedback"]["warning"] or pswd_check["feedback"]["suggestions"]:
            raise HTTPException(status_code=400, detail=f"Weak password:{pswd_check["feedback"]["warning"]} {" ".join(pswd_check["feedback"]["suggestions"])}")
        
        user_details = db.query(User).filter(User.id == user["id"]).first()
        user_details.username = new_user.username
        user_details.password = bcrypt_context.hash(new_user.password1)
        db.commit()
        db.refresh(user_details)
        return {"username": user_details.username}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/delete", response_model=ResponseUsername)
async def delete_user(user: auth_dependency, db: db_dependency):
    """
    ## Deletes the user whose token is provided

    ### Args:
    - **None**:

    ### Raises:
    - **HTTPException  400**: If the user is not found

    ### Returns:
    - **dict[str, str]**: A dictionary containing the username of the deleted user
    """
    try:
        user_details = db.query(User).filter(User.id == user["id"]).first()
        db.delete(user_details)
        db.commit()
        return {"username": user_details.username}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
###########################################################################################################
    
# Utility functions

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def authenticate_user(username: str, password: str, db: db_dependency) -> dict:
    """
    Authenticates a user.

    Args:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.
        db (Session): The database session to use for the authentication.

    Returns:
        dict | None: The user object if the authentication is successful, None otherwise.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    if not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return user

def create_access_token (username: str, user_id: str) -> str:
    """
    Generates a JWT access token for the given user.

    Args:
        username (str): The username of the user.
        user_id (str): The unique identifier of the user.

    Returns:
        str: The encoded JWT access token.
    """
    encode = {'sub': username, 'id': user_id}
    expires= datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)