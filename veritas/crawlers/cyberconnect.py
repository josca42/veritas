from veritas.crawlers.base import BaseCrawler
from pathlib import Path
import networkx as nx
from veritas.crawlers.utils import error_handling
from veritas import io
from datetime import datetime
from time import sleep
from gql.transport.exceptions import TransportQueryError


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

        self.G = nx.read_gpickle(graph_fp) if graph_fp else nx.DiGraph()
        self.articles_dir = Path("/home/ledger_of_record/data/mirror")

    def expand_graph(self, address):
        if address:
            connections = self.get_connections_for_address(address=address)
            self.add_connections(node=address, connections=connections)

        for i, (node, connections) in enumerate(self.traverse_graph()):
            self.add_connections(node, connections)

            if i % 500 == 0:
                print(i)
                nx.write_gpickle(
                    self.G,
                    f"/home/ledger_of_record/data/cyberconnect/social_graph_2.gpickle",
                )

    def traverse_graph(self):
        nodes = list(self.G.nodes(data=True))
        for node, metadata in nodes:
            if "q" in metadata:
                pass
            else:
                connections = self.get_connections_for_address(address=node)
                yield node, connections

    def add_connections(self, node, connections):
        self.G.add_node(node)
        self.G.nodes[node]["q"] = True

        if connections == TransportQueryError:
            self.G.nodes[node]["api_error"] = True
        else:
            for following in connections["followings"]["list"]:
                self.G.add_edge(node, following["address"])

            for follower in connections["followers"]["list"]:
                self.G.add_edge(follower["address"], node)

    @error_handling
    def get_connections_for_address(self, address):
        response = self.client.execute(self.query, variable_values={"address": address})
        return response["identity"]

    def crawl(self):

        while True:

            for fp in self.articles_dir.iterdir():
                article = io.json_reader(fp)
                address = article["authorship"]["contributor"]
                if address not in self.G.nodes:
                    self.expand_graph(address=address)

            self.expand_graph()


if __name__ == "__main__":
    CyberConnectCrawler(
        graph_fp="/home/ledger_of_record/data/cyberconnect/social_graph_2.gpickle"
    ).crawl()
    # from veritas import io
    # from pathlib import Path

    # addr = "0x4fF704F2c0B6330E0e55D029b787ce6F4"

    # crawler = CyberConnectCrawler(
    #     graph_fp="/home/ledger_of_record/data/cyberconnect/social_graph_2.gpickle"
    # )

    # a = 2

    # mirror_article_dir = Path("/home/ledger_of_record/data/mirror")
    # for fp in mirror_article_dir.iterdir():
    #     article = io.json_reader(fp)
    #     address = article["authorship"]["contributor"]
    #     break

    # a = 2
