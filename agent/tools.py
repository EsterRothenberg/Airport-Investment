from pathlib import Path

from services.airport_service import AirportService
from services.scoring_service import ScoringService


ANALYSIS_YEAR = 2025

airport_service = AirportService(
    t100_data_path=Path("data/t100/t100_2025.csv"),
    on_time_data_dir=Path("data/on_time"),
)

scoring_service = ScoringService()


def analyze_airport(
    airport_code: str,
) -> dict:
    metrics = airport_service.get_metrics(
        airport_code=airport_code,
        year=ANALYSIS_YEAR,
    )

    analysis = scoring_service.analyze(metrics)

    return {
        "airport_code": airport_code.upper(),
        "analysis_year": ANALYSIS_YEAR,
        "metrics": metrics.model_dump(),
        "analysis": analysis.model_dump(),
    }


def compare_airports(
    airport_codes: list[str],
) -> dict:
    if len(airport_codes) < 2:
        raise ValueError("At least two airport codes are required")

    results = {}

    for airport_code in airport_codes:
        results[airport_code.upper()] = analyze_airport(airport_code)

    return {
        "analysis_year": ANALYSIS_YEAR,
        "airports": results,
    }


def get_long_haul_analysis(
    airport_code: str,
) -> dict:

    airport_code = airport_code.upper().strip()

    routes = airport_service.t100_provider.get_routes(
        airport_code=airport_code,
        year=ANALYSIS_YEAR,
    )

    long_haul_share = airport_service.analytics_service.calculate_long_haul_share(
        routes
    )

    route_count = len({route.destination for route in routes})

    return {
        "airport_code": airport_code,
        "analysis_year": ANALYSIS_YEAR,
        "long_haul_share_pct": long_haul_share,
        "route_count": route_count,
        "assumptions": [
            "Long-haul routes are defined as nonstop segments of at least 3,000 miles."
        ],
    }


def rank_airports(
    airport_codes: list[str],
) -> list[dict]:
    if not airport_codes:
        return []

    results = []

    for airport_code in airport_codes:
        metrics = airport_service.get_metrics(
            airport_code=airport_code,
            year=ANALYSIS_YEAR,
        )

        analysis = scoring_service.analyze(metrics)

        results.append(
            {
                "airport_code": airport_code.upper(),
                "expansion_opportunity_score": analysis.expansion_opportunity_score,
                "demand_growth_score": analysis.demand_growth_score,
                "capacity_pressure_score": analysis.capacity_pressure_score,
                "operational_congestion_score": analysis.operational_congestion_score,
                "network_value_score": analysis.network_value_score,
                "assumptions": analysis.assumptions,
                "missing_data": analysis.missing_data,
            }
        )

    return sorted(
        results,
        key=lambda item: (
            item["expansion_opportunity_score"]
            if item["expansion_opportunity_score"] is not None
            else -1
        ),
        reverse=True,
    )
