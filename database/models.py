from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String)
    role = Column(String, default="user")  # user, admin, superadmin
    balance = Column(Integer, default=0)
    post_count = Column(Integer, default=0)

    channels = relationship("Channel", back_populates="owner")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(BigInteger, primary_key=True)
    title = Column(String)
    owner_id = Column(BigInteger, ForeignKey("users.id"))

    owner = relationship("User", back_populates="channels")

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    text = Column(String)
    is_active = Column(Boolean, default=True)
