from database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.sql.expression import null, text
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = "posts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer,primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    content = Column(String, nullable =False)
    published = Column(Boolean, server_default = 'TRUE', nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default = text("now()"))
    #this creates the foregin key 
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)

    owner = relationship("app.models.User")


class User(Base):
    __tablename__ = "users"
    #needed to add the line below when splitting up code
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,primary_key = True, nullable = False)
    email= Column(String, nullable = False, unique = True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default = text("now()") )

class Vote(Base):
    __tablename__ = 'votes'
    __table_args__ = {'extend_existing': True}
    user_id = Column(Integer, ForeignKey("users.id", ondelete ="CASCADE"), primary_key = True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete ="CASCADE"), primary_key = True)
