from pydantic import BaseModel, Field


class AirportMetrics(BaseModel):
    airport_code: str

    passenger_volume: int | None = None
    passenger_growth_pct: float | None = None

    departures: int | None = None
    flight_growth_pct: float | None = None

    load_factor_pct: float | None = None
    long_haul_share_pct: float | None = None

    delay_rate_pct: float | None = None
    cancellation_rate_pct: float | None = None

    route_count: int | None = None

    assumptions: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
