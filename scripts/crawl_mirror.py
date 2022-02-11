from veritas import crawlers, io
from pathlib import Path

# Initial cursor used: "WyIyMDIyLTAyLTEwVDEwOjE4OjMwLjA5NFoiLDFd"
data_dir = Path("data/mirror")
arweave_wallet_fp = (
    "wallets/arweave-keyfile-r8xG_s5cGl7TRnY3UmInLqQtWD8xOgJHs67Y4N0dmhc.json"
)
mirror = crawlers.Mirror(wallet_fp=arweave_wallet_fp)
cursor = "WyIyMDIyLTAyLTExVDA3OjEzOjQ0LjI3OVoiLDFd" 

t = 0
while True:
    for article in mirror.list_of_articles(after=cursor):
        article_data = mirror.article_data(id=article["id"])
        io.json_writer(data_dir / f"{article['id']}.json.lz4", article_data)

        t += 1
    print(f"Articles processed: {t}")

    cursor = article["cursor"]
