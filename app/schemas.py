from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint

class UserCreate(BaseModel):
    email:EmailStr
    password: str

#we do not want to send back the password
class UserOut(BaseModel):
    email:EmailStr
    id:str
    created_at:datetime
    class Config:
        orm_mode =True

class UserLogin(BaseModel):
    email:EmailStr
    password: str

class PostBase(BaseModel):
    title:str 
    content:str
    published : bool = True # this is  optional with a default value of True
    

#this extends the class PostBase and inherets all props
class PostCreate(PostBase):
    pass

#this inherets title, content, published from PostBase and adds id and created_at
class PostResponse(PostBase):
    id:int
    created_at:datetime
    owner_id: int
    owner: UserOut
    #tells the pydantic model to read the data even though is is not a dict
    class Config:
        orm_mode =True


class Token(BaseModel):
    access_token: str
    token_type:str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)