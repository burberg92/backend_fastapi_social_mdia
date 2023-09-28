from random import randrange
from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
import psycopg2 
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import time
from sqlalchemy.orm import Session
from database import engine, SessionLocal, get_db
import models
import schemas
import utils
from .routers import post, user



#These relative imports did not work did a workaround by absolute import
# from .database import engine, SessionLocal
# from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



# while loop in case it disconnects because of internet or something else
while True:
    try:
        conn = psycopg2.connect(
            host = 'localhost', 
            database ='fastapi', 
            user = 'postgres', 
            password = '1439752', 
            cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was sucessful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


my_posts = [{"title": "title of post 1", "content":"content of post 1", "id":1}, {"title": "title of post 2", "content":"content of post 2", "id":2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i 

app.include_router(post.router)
app.include_router(user.router)

@app.get('/')
async def root():
    return {'message':'hello world'}


#here added List[] because schemas.PostResponse is only for an individual post
@app.get('/posts', response_model=List[schemas.PostResponse])
async def get_posts(db:Session = Depends(get_db)):
    # using regular sql - the function does not need params
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts

@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db) ):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    #**post.dict() - this unpacks the dict and is equivalent to using title = post.title, content = post.content, etc...
    new_post = models.Post(**post.dict()) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #gets the new post from the db
    return new_post 

#note: be careful when you have a parameter {}, in this case if /posts/{id} was before than /posts/latest, /posts/latest would never be reached since it would think it is an id, ORDER MATTERS

@app.get('/posts/latest')
def get_latest():
    post = my_posts[-1]
    return post

@app.get('/posts/{id}', response_model=schemas.PostResponse)
def get_post(id: int, db:Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} was not found")
    return post

# we should use status code 204 whenever we delete a resource, we should not return anything when deleting except the Response/status code otherwise you will get an error
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} does not exsist")
    
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#updates the post
@app.put('/posts/{id}',response_model=schemas.PostResponse)
def update_post(id:int, updated_post:schemas.PostCreate,db:Session = Depends(get_db) ):

    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, (str(id))) )
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} was not found")
    
    post_query.update(updated_post.dict(), synchronize_session =False)
    db.commit()

    return post_query.first()



#creates a new user

@app.post('/users', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db:Session = Depends(get_db)):

    #hash the password - user.password 

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict()) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user) #gets the new post from the db
    return new_user 

@app.get('/users/{id}', response_model=schemas.UserOut)
def get_user(id:int, db:Session = Depends(get_db)):
    user= db.query(models.User).filter(models.User.id==id).first() #only one using first to not utlize more resources than needed

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} does not exsist")
    return user
