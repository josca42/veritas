from abc import ABCMeta, abstractmethod
from typing import Any
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import logging
from pathlib import Path


class BaseCrawler(metaclass=ABCMeta):
    def __init__(self, headers, url, log_fp, graphql_fp):
        self.logger = logging.basicConfig(
            filename=log_fp,
            format="%(asctime)s - %(message)s",
        )

        transport = AIOHTTPTransport(url=url, headers=headers)
        self.client = Client(transport=transport)
        self.query = self._load_graphql_query(graphql_fp)

    @staticmethod
    def _load_graphql_query(path):
        with open(path) as f:
            return gql(f.read())

    @abstractmethod
    def crawl() -> None:
        pass
