from providers.airport_metadata_provider import (
    AirportMetadataProvider,
)
from services.airport_resolver import AirportResolver


def create_resolver():
    provider = AirportMetadataProvider(
        "data/metadata/airports.csv"
    )

    return AirportResolver(
        provider
    )


def test_resolve_sfo_by_code():
    resolver = create_resolver()

    airport = resolver.resolve_code(
        "SFO"
    )

    assert airport is not None
    assert airport.iata_code == "SFO"
    assert airport.state_code == "CA"


def test_resolve_code_is_case_insensitive():
    resolver = create_resolver()

    airport = resolver.resolve_code(
        "sfo"
    )

    assert airport is not None
    assert airport.iata_code == "SFO"


def test_find_airports_by_state():
    resolver = create_resolver()

    airports = resolver.find_by_states(
        ["CA"]
    )

    assert len(airports) > 0

    assert all(
        airport.state_code == "CA"
        for airport in airports
    )


def test_unknown_airport_returns_none():
    resolver = create_resolver()

    airport = resolver.resolve_code(
        "XYZ"
    )

    assert airport is None
