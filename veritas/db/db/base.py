# Import all the models, so that Base has them before being
# imported by Alembic
from veritas.db.db.base_class import Base  # noqa
from veritas.db.models import Article  # noqa
