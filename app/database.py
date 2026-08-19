import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For production on Azure, set DATABASE_URL to a Postgres connection string.
# Defaults to a local SQLite file for easy dev/testing.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./career_hub.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
