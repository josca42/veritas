from .base import BaseCrawler
from pathlib import Path
import networkx as nx
from .utils import retry
from veritas import io
from datetime import datetime


class CyberConnectCrawler(BaseCrawler):
    def __init__(self, graph_fp=None):
        super().__init__(
            headers={
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "application/json",
                "Connection": "keep-alive",
                "DNT": "1",
                "Origin": "https://api.cybertino.io",
            },
            url="https://api.cybertino.io/connect/",
            log_fp="/home/ledger_of_record/data/logs/cyberconnect.log",
            graphql_fp=Path(__file__).parent / "graphql_queries/cyberconnect.graphql",
        )

        self.G = nx.read_gpickle(graph_fp) if graph_fp else nx.DiGraph
        self.articles_dir = Path("data/mirror")

    def expand_graph(self, address):
        if address:
            connections = self.get_connections_for_address(address=address)
            self.add_connections(connections, node=connections["address"])

        while True:
            for i, connections in enumerate(self.traverse_graph()):
                self.add_connections(connections, node=connections["address"])

                if i % 1000 == 0:
                    print(i)

                    timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
                    nx.write_gpickle(
                        self.G,
                        f"/home/ledger_of_record/data/cyberconnect/social_graph_{timestamp}.gpickle",
                    )

    def traverse_graph(self):
        for node, metadata in self.G.nodes(data=True):
            if "q" in metadata:
                pass
            else:
                connections = self.get_connections_for_address(address=node)
                yield connections

    def add_connections(self, connections, node):
        for following in connections["followings"]["list"]:
            self.G.add_edge(node, following["address"])

        for follower in connections["followers"]["list"]:
            self.G.add_edge(follower["address"], node)

        self.G.nodes[node]["q"] = True

    @retry
    def get_connections_for_address(self, address):
        response = self.client.execute(self.query, address=address)
        connections = response["data"]["identity"]
        return connections

    def crawl(self):

        while True:
            for fp in self.articles_dir.iterdir():
                article = io.json_reader(fp)
                address = article["authorship"]
                if address not in self.G.nodes:
                    self.expand_graph(address=address)

            self.expand_graph()
