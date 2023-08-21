from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    # admin_id = Column(Integer, ForeignKey("users.id"))

    # admin = relationship("Users", back_populates="admin")
    tag = relationship("Tags", back_populates="owner")
    association = relationship("Associations", back_populates="user")


class Tags(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    popular = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="tag")
    association = relationship("Associations", back_populates="tag")


class Associations(Base):
    __tablename__ = "user_tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))
    ratings = Column(Integer, default=1)

    user = relationship("Users", back_populates="association")
    tag = relationship("Tags", back_populates="association")
