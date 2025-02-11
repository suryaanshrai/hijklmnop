from pydantic import BaseModel

class ResponseUsername(BaseModel):
    username: str

class ResponseUser(ResponseUsername):
    access_token: str

class CreateUser(BaseModel):
    username: str
    password1: str
    password2: str

class LoginUser(BaseModel):
    username: str
    password: str
    
class UpdateUser(BaseModel):
    username: str
    password1: str
    password2: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str