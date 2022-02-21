from pathlib import Path
import pickle
from dotenv import dotenv_values
from .base import json_reader, json_writer
from veritas import config

articles_dir = config["articles_dir"]
metadata_types = ["ner", "pos", "summary", "embedding", "cursor"]


def load_metadata(source: str, article_id: str, metadata_type: str):
    fp = articles_dir / source / article_id / f"{metadata_type}.pickle"
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

    fp = articles_dir / source / article_id / f"{metadata_type}.pickle"
    with fp.open("wb") as f:
        pickle.dump(obj, f)


def load_article(source: str, article_id: str):
    fp = articles_dir / source / article_id / "article.json.lz4"
    article = json_reader(fp)
    return article


def save_article(article, source: str, article_id: str):
    article_dir = articles_dir / source / article_id
    fp = article_dir / "article.json.lz4"

    articles_dir.mkdir(parents=True, exist_ok=True)
    json_writer(fp, article)
