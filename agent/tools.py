from pathlib import Path

from services.airport_service import AirportService
from services.scoring_service import ScoringService
from providers.airport_metadata_provider import (
    AirportMetadataProvider,
)
from services.airport_resolver import (
    AirportResolver,
)

ANALYSIS_YEAR = 2025


def _validate_airport_code(airport_code: str) -> None:
    normalized = airport_code.strip().upper() if airport_code else ""
    
    if len(normalized) != 3:
        raise ValueError(
            f"Invalid airport code '{airport_code}'. "
            "Use 3-letter IATA code (e.g., LAX, JFK, SFO)."
        )
    
    if not normalized.isalpha():
        raise ValueError(
            f"Invalid airport code '{airport_code}'. "
            "Use 3-letter IATA code (e.g., LAX, JFK, SFO)."
        )


airport_service = AirportService(
    t100_data_path=Path("data/t100/t100_2025.csv"),
    on_time_data_dir=Path("data/on_time"),
)
metadata_provider = AirportMetadataProvider("data/metadata/airports.csv")

airport_resolver = AirportResolver(metadata_provider)
scoring_service = ScoringService()


def analyze_airport(
    airport_code: str,
) -> dict:
    _validate_airport_code(airport_code)
    
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
    
    for code in airport_codes:
        _validate_airport_code(code)

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
    _validate_airport_code(airport_code)
    
    airport_code = airport_code.upper().strip()

    routes = airport_service.t100_provider.get_routes(
        airport_code=airport_code,
        year=ANALYSIS_YEAR,
    )

    if not routes:
        return {
            "airport_code": airport_code,
            "analysis_year": ANALYSIS_YEAR,
            "long_haul_share_pct": None,
            "total_departures": 0,
            "long_haul_departures": 0,
            "route_count": 0,
            "assumptions": [
                "Long-haul routes are defined as nonstop "
                "segments of at least 3,000 miles."
            ],
            "missing_data": ["route-level traffic data"],
        }

    total_departures = sum(route.departures or 0 for route in routes)

    long_haul_departures = sum(
        route.departures or 0
        for route in routes
        if (route.distance_miles is not None and route.distance_miles >= 3000)
    )

    long_haul_share = (
        round(
            long_haul_departures / total_departures * 100,
            2,
        )
        if total_departures > 0
        else None
    )

    route_count = len({route.destination for route in routes if route.destination})

    return {
        "airport_code": airport_code,
        "analysis_year": ANALYSIS_YEAR,
        "long_haul_share_pct": long_haul_share,
        "total_departures": total_departures,
        "long_haul_departures": long_haul_departures,
        "route_count": route_count,
        "assumptions": [
            "Long-haul routes are defined as nonstop segments of at least 3,000 miles.",
            "Long-haul share is calculated using performed "
            "passenger-service departures, not the number of routes.",
        ],
        "missing_data": [],
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
                "data_completeness_pct": analysis.data_completeness_pct,
                "market_scale_score": analysis.market_scale_score,
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


def find_airports(
    states: list[str] | None = None,
    city: str | None = None,
    airport_code: str | None = None,
    name_query: str | None = None,
) -> dict:
    airports = []

    if airport_code:
        airport = airport_resolver.resolve_code(airport_code)

        if airport:
            airports = [airport]

    elif city:
        airports = airport_resolver.find_by_city(city)

    elif name_query:
        airports = airport_resolver.find_by_name(name_query)

    elif states:
        airports = airport_resolver.find_by_states(states)

    else:
        return {
            "airports": [],
            "error": ("Provide airport_code, city, name_query, or states."),
        }

    return {
        "count": len(airports),
        "airports": [airport.model_dump() for airport in airports],
    }


def rank_airports_by_geography(
    states: list[str],
    max_airports: int = 20,
) -> list[dict]:
    airports = airport_resolver.find_by_states(states)

    if not airports:
        return []

    # Important:
    # Metadata may include airports for which our BTS/T100
    # analytical sources don't have sufficient data.
    results = []

    for airport in airports:
        try:
            metrics = airport_service.get_metrics(
                airport_code=airport.iata_code,
                year=ANALYSIS_YEAR,
            )

            analysis = scoring_service.analyze(metrics)

            results.append(
                {
                    "airport_code": airport.iata_code,
                    "airport_name": airport.name,
                    "city": airport.city,
                    "state": airport.state_code,
                    "expansion_opportunity_score": analysis.expansion_opportunity_score,
                    "data_completeness_pct": analysis.data_completeness_pct,
                    "demand_growth_score": analysis.demand_growth_score,
                    "capacity_pressure_score": analysis.capacity_pressure_score,
                    "operational_congestion_score": analysis.operational_congestion_score,
                    "network_value_score": analysis.network_value_score,
                    "market_scale_score": analysis.market_scale_score,
                    "missing_data": analysis.missing_data,
                }
            )

        except Exception:
            # Airport exists in metadata but does not have
            # enough analytical coverage for this prototype.
            continue

    results.sort(
        key=lambda item: (
            item["expansion_opportunity_score"]
            if item["expansion_opportunity_score"] is not None
            else -1
        ),
        reverse=True,
    )

    return results[:max_airports]
