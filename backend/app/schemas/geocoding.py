from pydantic import BaseModel


class ReverseGeocodeResponse(BaseModel):
    formatted_address: str | None = None
    street: str | None = None
    house_number: str | None = None
    postal_code: str | None = None
    city: str | None = None
    source: str
    message: str | None = None
