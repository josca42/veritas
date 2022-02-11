from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pickle
import arweave
from arweave.arweave_lib import Transaction
import json
from pathlib import Path


class MirrorCrawler:
    def __init__(self, wallet_fp):
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "keep-alive",
            "DNT": "1",
            "Origin": "https://arweave.net",
        }
        url = "https://arweave.net/graphql"
        transport = AIOHTTPTransport(url=url, headers=headers)

        self.client = Client(transport=transport)
        self.query = self._load_graphql_query(
            Path(__file__).parent / "articles_query.graphql"
        )
        self.wallet = arweave.Wallet(wallet_fp)

    def list_of_articles(self, after, first=20):
        vars = {"first": first, "after": after}
        articles = self.client.execute(self.query, variable_values=vars)
        for article in articles["transactions"]["edges"]:
            Id = article["node"]["id"]
            cursor = article["cursor"]
            yield {"id": Id, "cursor": cursor}

    @staticmethod
    def _load_graphql_query(path):
        with open(path) as f:
            return gql(f.read())

    def article_data(self, id):
        tx = Transaction(self.wallet, id="N_nQi_IoFdCG02Ka8RhEd3xp2QZHIkA3bSIL_H6UwhM")
        tx.get_data()
        return json.loads(tx.data)


if __name__ == "__main__":
    mirror = MirrorCrawler()

    for article in mirror.articles(after="WyIyMDIyLTAyLTEwVDEwOjE4OjMwLjA5NFoiLDFd"):
        article_data = mirror.article_data(id=article["id"])

    a = 2

    wallet_file_path = (
        "wallets/arweave-keyfile-r8xG_s5cGl7TRnY3UmInLqQtWD8xOgJHs67Y4N0dmhc.json"
    )
    wallet = arweave.Wallet(wallet_file_path)
    tx = Transaction(wallet, id="N_nQi_IoFdCG02Ka8RhEd3xp2QZHIkA3bSIL_H6UwhM")
    tx.get_data()
    data = json.loads(tx.data)
# pickle.dump(response, open("response.p", "wb"))
