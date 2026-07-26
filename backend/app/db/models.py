from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    watchlist = relationship("WatchlistItem", back_populates="user")
    chat_sessions = relationship(
        "ChatSession",
        back_populates="user"
    )

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key= True, autoincrement=True)
    tmdb_id = Column(Integer, unique = True, nullable=False)
    title = Column(String(500),nullable = False)
    overview = Column(Text)
    poster_path = Column(String(255))
    release_date = Column(String(20))
    runtime = Column(Integer)
    genres = Column(JSONB)
    vote_average = Column(Float)
    overview_embedding = Column(Vector(384))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WatchlistItem(Base):
   __tablename__ = "watchlist"

   id = Column(Integer, primary_key=True,
    autoincrement=True)
   user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
   movie_id = Column(Integer, ForeignKey("movies.id"), nullable=True)
   status=Column(String(50),default="want_to_watch")
   rating=Column(Integer)
   added_at = Column(DateTime(timezone=True), server_default=func.now())

   __table_args__ = (
       UniqueConstraint("user_id", "movie_id", name="unique_movie_user"),
   )

   user = relationship("User", back_populates = "watchlist")
   movie = relationship("Movie")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default = "New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"),nullable=False)
    role = Column(String(50), nullable= False)
    content=Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")