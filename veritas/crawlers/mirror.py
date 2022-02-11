from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pickle
import arweave
from arweave.arweave_lib import Transaction
import json
from pathlib import Path
import logging
from .utils import retry


class MirrorCrawler:
    def __init__(self, wallet_fp):

        logging.basicConfig(
            filename="/home/ledger_of_record/data/logs/mirror.log", 
            format="%(asctime)s - %(message)s"
            )

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
            Path(__file__).parent / "mirror_query.graphql"
        )
        self.wallet = arweave.Wallet(wallet_fp)
        
        
    @retry
    def list_of_articles(self, after, first=100):
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

    @retry
    def article_data(self, id):
        tx = Transaction(self.wallet, id=id)
        tx.get_data()
        return json.loads(tx.data)

    
