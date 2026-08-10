from models.traffic import AirportTraffic, RouteTraffic
from services.analytics_service import AnalyticsService


def test_calculate_growth():
    result = AnalyticsService.calculate_growth(
        current=110,
        previous=100,
    )

    assert result == 10.0


def test_calculate_growth_returns_none_for_zero_previous():
    result = AnalyticsService.calculate_growth(
        current=110,
        previous=0,
    )

    assert result is None


def test_calculate_load_factor():
    result = AnalyticsService.calculate_load_factor(
        passengers=80,
        seats=100,
    )

    assert result == 80.0


def test_calculate_long_haul_share():
    routes = [
        RouteTraffic(
            origin="ANC",
            destination="SEA",
            year=2025,
            distance_miles=1500,
            departures=100,
        ),
        RouteTraffic(
            origin="ANC",
            destination="JFK",
            year=2025,
            distance_miles=3400,
            departures=25,
        ),
    ]

    result = AnalyticsService.calculate_long_haul_share(
        routes
    )

    assert result == 20.0
