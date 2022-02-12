from veritas import crawlers, io
from pathlib import Path

mirror_data = Path("data/mirror")
mirror = crawlers.Mirror(wallet_fp=arweave_wallet_fp)
cursor = "WyIyMDIyLTAyLTExVDA3OjEzOjQ0LjI3OVoiLDFd"
