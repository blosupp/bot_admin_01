from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}  # 👈 обязательно для перезапуска

    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    role = Column(String, default="client")
    balance = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    use_memory = Column(Boolean, default=True)  # ✅ добавили

    channels = relationship("Channel", back_populates="owner")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    channel_id = Column(BigInteger, nullable=False, unique=True)  # ← добавляем это
    owner_id = Column(BigInteger, ForeignKey("users.id"))

    owner = relationship("User", back_populates="channels")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    text = Column(String)
    is_active = Column(Boolean, default=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    role = Column(String)  # 'user' или 'assistant'
    content = Column(String)

class TempPost(Base):
    __tablename__ = "temp_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    file_id = Column(String)
    caption = Column(String)  # итоговый текст
    original = Column(String)  # исходная подпись от пользователя
