from sqlalchemy.sql.sqltypes import Boolean
from veritas.db.db.base_class import Base
from sqlalchemy import Column, Float, Integer, String, Boolean, null


class Article(Base):
    __tablename__ = "articles"  # type: ignore

    id = Column(String(length=43), primary_key=True, nullable=False)
    source = Column(String, primary_key=True, nullable=False)
    ner = Column(Boolean, default=False)
    pos = Column(Boolean, default=False)
    summary = Column(Boolean, default=False)
    language = Column(String, default="Missing")
    embedding = Column(Boolean, default=False)
    author = Column(String, default="Missing")

    ## Add an extra column that timestamps when each
    ## observation is saved to db table
