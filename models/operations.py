from pydantic import BaseModel, Field


class AirportOperations(BaseModel):
    airport_code: str
    year: int
    month: int | None = None

    scheduled_flights: int
    completed_flights: int
    delayed_flights: int
    cancelled_flights: int

    delay_rate_pct: float | None = None
    cancellation_rate_pct: float | None = None

    assumptions: list[str] = Field(default_factory=list)