from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime

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


class ScheduledPost(Base):
    """
    🗂 Модель для хранения отложенных публикаций
    """
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)         # кто создал пост
    channel_id = Column(BigInteger)                  # куда публиковать
    caption = Column(String, nullable=True)          # текст поста
    file_id = Column(String, nullable=True)          # если есть фото
    scheduled_time = Column(DateTime)                # дата и время публикации
    sent = Column(Boolean, default=False)            # опубликован ли
    created_at = Column(DateTime, default=datetime.utcnow)  # когда создан


class ActionLog(Base):
    """
    📄 Таблица логов действий пользователей
    """
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    action_type = Column(String)  # например: 'generate', 'publish', 'delete', 'login'
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)