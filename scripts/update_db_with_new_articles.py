from veritas.db import crud
from veritas import config
from tqdm import tqdm

articles_dir = config["articles_dir"]


def update_db_with_new_articles():
    for articles_source in articles_dir.iterdir():
        articles_in_db = crud.article.list_articles_in_db(source=articles_source.name)
        articles_in_folder = {
            article_folder.name for article_folder in articles_source.iterdir()
        }
        new_articles = articles_in_folder - articles_in_db

        for article_id in tqdm(new_articles, desc=articles_source.name):
            crud.article.create({"id": article_id, "source": articles_source.name})


if __name__ == "__main__":
    update_db_with_new_articles()
