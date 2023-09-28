from app import oauth2, schemas, models


from typing import Optional, List
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

router = APIRouter(
    prefix="/posts", 
    tags=['Posts']
)

#here added List[] because schemas.PostResponse is only for an individual post
#limit is our query parameter to limit the number of responses, 
# skip is another parameter to skip to the next queries
# seach is another parameter to search by title
@router.get('/', response_model=List[schemas.PostResponse])
async def get_all_posts(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip = 0, search: Optional[str] =""):
    # using regular sql - the function does not need params
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

#here added List[] because schemas.PostResponse is only for an individual post
@router.get('/owner', response_model=List[schemas.PostResponse])
async def get_owner_posts(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # using regular sql - the function does not need params
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    return posts

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db),current_user:int= Depends(oauth2.get_current_user) ):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    #**post.dict() - this unpacks the dict and is equivalent to using title = post.title, content = post.content, etc..., we also have to add owner_id bc the response_model expects it 
    new_post = models.Post(owner_id=current_user.id , **post.dict()) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #gets the new post from the db
    return new_post 

#note: be careful when you have a parameter {}, in this case if /posts/{id} was before than /posts/latest, /posts/latest would never be reached since it would think it is an id, ORDER MATTERS


@router.get('/{id}', response_model=schemas.PostResponse)
def get_post(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} was not found")
    return post

# we should use status code 204 whenever we delete a resource, we should not return anything when deleting except the Response/status code otherwise you will get an error
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    #checks to see if post exsists 
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} does not exsist")
    #checks to see if owner is person logged in
    if post.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail = "Not authorized to perform requested action")
    
    post_query.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#updates the post
@router.put('/{id}',response_model=schemas.PostResponse)
def update_post(id:int, updated_post:schemas.PostCreate,db:Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):

    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, (str(id))) )
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    #checks to see if post exsists 
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} was not found")
    #checks to see if owner is person logged in
    if post.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail = "Not authorized to perform requested action")
    
    post_query.update(updated_post.dict(), synchronize_session =False)
    db.commit()

    return post_query.first()
