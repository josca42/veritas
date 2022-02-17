from veritas import io, nlp
from veritas.db import crud
from tqdm import tqdm


def update_author():
    df_articles = crud.article.filter(filters={"author": "Missing"})
    for idx, article_row in tqdm(df_articles.iterrows(), total=len(df_articles)):
        article = io.load_article(
            source=article_row["source"], article_id=article_row["id"]
        )

        Id = article_row["id"]
        source = article_row["source"]
        author = article["authorship"]["contributor"]

        update = {"id": Id, "source": source, "author": author}
        crud.article.update(update)


def update_language():
    df_articles = crud.article.filter(filters={"language": "Missing"})
    for idx, article_row in tqdm(df_articles.iterrows(), total=len(df_articles)):
        article = io.load_article(
            source=article_row["source"], article_id=article_row["id"]
        )

        Id = article_row["id"]
        source = article_row["source"]
        text = article["content"]["body"]

        lang = nlp.language_detect(text)

        update = {"id": Id, "source": source, "language": lang}
        crud.article.update(update)


def update_metadata():
    df_articles = crud.article.filter(filters={"ner": False, "language": "en"})
    for idx, article_row in tqdm(df_articles.iterrows(), total=len(df_articles)):
        article = io.load_article(
            source=article_row["source"], article_id=article_row["id"]
        )

        Id = article_row["id"]
        source = article_row["source"]
        text = article["content"]["body"]

        embedding = nlp.embed(text)
        ner = nlp.NER(text)
        pos = nlp.POS(text)

        io.save_metadata(ner, source=source, article_id=Id, metadata_type="ner")
        io.save_metadata(pos, source=source, article_id=Id, metadata_type="pos")
        io.save_metadata(
            embedding, source=source, article_id=Id, metadata_type="embedding"
        )

        update = {
            "id": Id,
            "source": source,
            "ner": True,
            "pos": True,
            "embedding": True,
        }
        crud.article.update(update)


if __name__ == "__main__":
    update_author()
    update_language()
    update_metadata()
