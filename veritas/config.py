from dotenv import dotenv_values
from pathlib import Path

config = dotenv_values()
data_dir = Path(config["DATA_DIR"])
config["sqlite_db_fp"] = data_dir / "db" / "sqlite_articles.db"
config["articles_dir"] = data_dir / "articles"
config["models_dir"] = data_dir / "models"
