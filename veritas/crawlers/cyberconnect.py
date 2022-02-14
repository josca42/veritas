from veritas.crawlers.base import BaseCrawler
from pathlib import Path
import networkx as nx
from veritas.crawlers.utils import retry
from veritas import io
from datetime import datetime
from time import sleep


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
            self.add_connections(connections)

        for i, connections in enumerate(self.traverse_graph()):
            self.add_connections(connections)

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
                yield connections

    def add_connections(self, connections):
        node = connections["address"]
        self.G.add_node(node)
        for following in connections["followings"]["list"]:
            self.G.add_edge(node, following["address"])

        for follower in connections["followers"]["list"]:
            self.G.add_edge(follower["address"], node)

        self.G.nodes[node]["q"] = True

    @retry
    def get_connections_for_address(self, address):
        response = self.client.execute(self.query, variable_values={"address": address})
        return response["identity"]

    def crawl(self):

        # last_error_timestamp = datetime.now()
        # t = 0

        while True:
            # try:
            for fp in self.articles_dir.iterdir():
                article = io.json_reader(fp)
                address = article["authorship"]["contributor"]
                if address not in self.G.nodes:
                    self.expand_graph(address=address)

            self.expand_graph()

            # except Exception as e:
            #     print(e)
            #     self.logger.info(e)
            #     sleep(10)

            #     # Try again 3 times. If error not resolved break out of loop
            #     error_timestamp = datetime.now()
            #     if (error_timestamp - last_error_timestamp) < 60 * 10:
            #         t += 1
            #         if t == 3:
            #             break
            #     elsed:
            #         t = 0


if __name__ == "__main__":
    CyberConnectCrawler(
        graph_fp="/home/ledger_of_record/data/cyberconnect/social_graph_2.gpickle"
    ).crawl()
    # from veritas import io
    # from pathlib import Path

    # crawler = CyberConnectCrawler(
    #     graph_fp="/home/ledger_of_record/data/cyberconnect/social_graph_2.gpickle"
    # )

    # mirror_article_dir = Path("/home/ledger_of_record/data/mirror")
    # for fp in mirror_article_dir.iterdir():
    #     article = io.json_reader(fp)
    #     address = article["authorship"]["contributor"]
    #     break

    # a = 2
