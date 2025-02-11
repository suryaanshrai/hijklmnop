from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.schemas.user import User
from app.config import ALGORITHM, SECRET_KEY
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.dependencies.database import db_dependency


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db:db_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None or db.query(User).filter(User.id == user_id).first() is None:
            raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user. ')
    
auth_dependency = Annotated[dict, Depends(get_current_user)]