from .. import models
from .. import schemas
from .. import utils


from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

router = APIRouter()

#creates a new user

@router.post('/users', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db:Session = Depends(get_db)):

    #hash the password - user.password 

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict()) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user) #gets the new post from the db
    return new_user 

@router.get('/users/{id}', response_model=schemas.UserOut)
def get_user(id:int, db:Session = Depends(get_db)):
    user= db.query(models.User).filter(models.User.id==id).first() #only one using first to not utlize more resources than needed

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} does not exsist")
    return user
