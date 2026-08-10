from pydantic import BaseModel, Field


class AirportAnalysis(BaseModel):
    airport_code: str

    demand_growth_score: float | None = None
    capacity_pressure_score: float | None = None
    operational_congestion_score: float | None = None
    network_value_score: float | None = None

    expansion_opportunity_score: float | None = None

    assumptions: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
