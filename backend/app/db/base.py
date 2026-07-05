from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Alle SQLAlchemy-Modelle hier importieren, damit Alembic sie erkennt.
# Beispiel (ab Sprint 2):
# from app.models import user, organization  # noqa: F401
