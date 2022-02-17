from pathlib import Path
import pickle
from dotenv import dotenv_values
from .base import json_reader, json_writer
from veritas import config

article_dir = config["articles_dir"]
metadata_types = ["ner", "pos", "summary", "embedding"]


def load_metadata(source: str, article_id: str, metadata_type: str):
    fp = article_dir / source / article_id / f"{metadata_type}.p"
    if fp.is_file():
        with fp.open("rb") as f:
            obj = pickle.load(f)
        return obj
    else:
        return None


def save_metadata(obj, source: str, article_id: str, metadata_type: str):
    assert metadata_type in metadata_types, (
        f"metadata_type {metadata_type} not recognized. Known metadata types are {metadata_types}.\n"
        "Update known metadata types if introducing a new metadata type."
    )

    fp = article_dir / source / article_id / f"{metadata_type}.p"
    with fp.open("wb") as f:
        pickle.dump(obj, f)


def load_article(source: str, article_id: str):
    fp = article_dir / source / article_id / "article.json.lz4"
    article = json_reader(fp)
    return article


def save_article(article, source: str, article_id: str):
    fp = article_dir / source / article_id / "article.json.lz4"
    json_writer(fp, article)
