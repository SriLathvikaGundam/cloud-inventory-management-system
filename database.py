from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the connection string. "sqlite:///./inventory.db" means:
# use SQLite, and store the database in a file called inventory.db
# right here in this project folder.
DATABASE_URL = "sqlite:///./inventory.db"

# The "engine" is the actual connection to the database.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory that creates new "sessions" —
# a session is basically a temporary workspace you use to
# talk to the database (add data, query data, etc.)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a special class that all our table models will inherit from.
# SQLAlchemy uses this to know which Python classes represent database tables.
Base = declarative_base()