import arweave
from arweave.arweave_lib import Transaction
import json
from pathlib import Path
from veritas.crawlers.utils import error_handling, latest_file_in_folder
from veritas import io, config
from veritas.db import crud
from veritas.crawlers.base import BaseCrawler

mirror_articles_dir = config["articles_dir"] / "mirror"
mirror_crawler_log = config["logs_dir"] / "mirror.log"


class MirrorCrawler(BaseCrawler):
    def __init__(self, wallet_fp):
        super().__init__(
            headers={
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Connection": "keep-alive",
                "DNT": "1",
                "Origin": "https://arweave.net",
            },
            url="https://arweave.net/graphql",
            log_fp=mirror_crawler_log,
            graphql_fp=Path(__file__).parent / "graphql_queries/mirror.graphql",
        )

        self.wallet = arweave.Wallet(wallet_fp)
        self.storage_dir = mirror_articles_dir
        self.latest_article_id_crawled = None

    def list_of_articles(self, after, first=100):
        vars = {"first": first, "after": after}
        articles = self.get_articles(vars=vars)
        for article in articles["transactions"]["edges"]:
            Id = article["node"]["id"]
            cursor = article["cursor"]
            yield {"id": Id, "cursor": cursor}

    @error_handling
    def article_data(self, id):
        tx = Transaction(self.wallet, id=id)
        tx.get_data()
        return json.loads(tx.data)

    @error_handling
    def get_articles(self, vars):
        return self.client.execute(self.query, variable_values=vars)

    def crawl_from_next_article(self, skip_article=False):

        if self.latest_article_id_crawled:
            article_id = self.latest_article_id_crawled
        else:
            fp = latest_file_in_folder(self.storage_dir)
            article_id = fp.name

        cursor = io.load_metadata(
            source="mirror", article_id=article_id, metadata_type="cursor"
        )
        if skip_article:
            articles = list(self.list_of_articles(after=cursor, first=2))
            article = articles[-1]
            return article["cursor"]
        else:
            return cursor

    def crawl(self, skip_article=False):
        cursor = self.crawl_from_next_article(skip_article)
        t = 0
        while True:
            try:
                for article in self.list_of_articles(after=cursor):
                    article_exists = crud.article.exists(id=article["id"])
                    if not article_exists:
                        article_data = self.article_data(id=article["id"])
                        io.save_article(
                            article=article_data,
                            source="mirror",
                            article_id=article["id"],
                        )
                        # Save cursor for check marking purposes
                        io.save_metadata(
                            article["cursor"],
                            source="mirror",
                            article_id=article["id"],
                            metadata_type="cursor",
                        )
                        crud.article.create({"id": article["id"], "source": "mirror"})

                        self.latest_article_id_crawled = article["id"]
                        t += 1
                    else:
                        continue
            except Exception as e:
                print(e)
                self.logger.info(f"last id crawled: {self.latest_article_id_crawled}")
                self.logger.info(e)
                self.crawl(skip_article=True)

            cursor = article["cursor"]
            print(f"Articles processed: {t}")


if __name__ == "__main__":
    MirrorCrawler(wallet_fp="/home/ledger_of_record/wallets/arweave.json").crawl()
