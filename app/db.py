from sqlalchemy import (
    create_engine, Column, Integer, String,
    Boolean, DateTime, Text
)
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./jobs.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    web_search = Column(Boolean, default=False)
    image_gen = Column(Boolean, default=False)
    deep_research = Column(Boolean, default=False)
    status = Column(String, default="pending", index=True)
    result = Column(Text, nullable=True)
    mode = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

def init_db():
    Base.metadata.create_all(bind=engine)
