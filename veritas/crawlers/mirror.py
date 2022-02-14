import arweave
from arweave.arweave_lib import Transaction
import json
from pathlib import Path
from veritas.crawlers.utils import error_handling, latest_file_in_folder
from veritas import io
from veritas.crawlers.base import BaseCrawler


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
            log_fp="/home/ledger_of_record/data/logs/mirror.log",
            graphql_fp=Path(__file__).parent / "graphql_queries/mirror.graphql",
        )

        self.wallet = arweave.Wallet(wallet_fp)
        self.storage_dir = Path("/home/ledger_of_record/data/mirror")

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
        fp = latest_file_in_folder(self.storage_dir)

        cursor = fp.name.split(".")[1]
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
                articles = list(self.storage_dir.iterdir())
                for article in self.list_of_articles(after=cursor):
                    fp = (
                        self.storage_dir
                        / f"{article['id']}.{article['cursor']}.json.lz4"
                    )
                    if fp not in articles:
                        article_data = self.article_data(id=article["id"])
                        io.json_writer(fp, article_data)
                        t += 1
                    else:
                        continue
            except Exception as e:
                print(e)
                self.crawl(skip_article=True)

            cursor = article["cursor"]
            print(f"Articles processed: {t}")


if __name__ == "__main__":
    MirrorCrawler(wallet_fp="/home/ledger_of_record/wallets/arweave.json").crawl()
