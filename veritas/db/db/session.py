from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from veritas import config

sqlite_db_fp = config["sqlite_db_fp"]

SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_db_fp}"
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
