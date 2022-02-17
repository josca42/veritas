from sqlalchemy.orm import Session
from veritas.db.db.session import engine
from veritas.db.db.base import Base  # noqa: F401


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db() -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables using the line below
    Base.metadata.create_all(bind=engine)
