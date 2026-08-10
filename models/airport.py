from pydantic import BaseModel


class Airport(BaseModel):
    iata_code: str
    name: str

    city: str | None = None
    state_code: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    airport_type: str | None = None
    scheduled_service: bool = False
