from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Alle SQLAlchemy-Modelle hier importieren, damit Alembic sie erkennt.
from app.models import user, organization, membership, trusted_relationship, mobility_profile, vehicle, driver_profile, transport_request, driver_shift  # noqa: F401, E402
