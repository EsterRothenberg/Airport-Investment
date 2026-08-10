from pydantic import BaseModel, Field


class AirportTraffic(BaseModel):
    airport_code: str
    year: int
    month: int | None = None

    passengers: int | None = None
    seats: int | None = None
    departures: int | None = None

    load_factor_pct: float | None = None


class RouteTraffic(BaseModel):
    origin: str
    destination: str

    year: int
    month: int | None = None

    distance_miles: float | None = None
    passengers: int | None = None
    seats: int | None = None
    departures: int | None = None


class AirportTrafficHistory(BaseModel):
    airport_code: str
    records: list[AirportTraffic] = Field(default_factory=list)
