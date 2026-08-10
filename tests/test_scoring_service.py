from models.metrics import AirportMetrics
from services.scoring_service import ScoringService


def create_complete_metrics():
    return AirportMetrics(
        airport_code="TEST",
        passenger_volume=10_000_000,
        passenger_growth_pct=5.0,
        departures=100_000,
        flight_growth_pct=5.0,
        load_factor_pct=80.0,
        long_haul_share_pct=10.0,
        delay_rate_pct=15.0,
        cancellation_rate_pct=1.0,
        route_count=100,
    )


def test_normalize():
    scoring = ScoringService()

    result = scoring.normalize(
        value=50,
        low=0,
        high=100,
    )

    assert result == 50.0


def test_normalize_clamps_above_100():
    scoring = ScoringService()

    result = scoring.normalize(
        value=150,
        low=0,
        high=100,
    )

    assert result == 100.0


def test_complete_data_has_100_percent_completeness():
    scoring = ScoringService()

    metrics = create_complete_metrics()

    analysis = scoring.analyze(
        metrics
    )

    assert analysis.data_completeness_pct == 100.0

    assert (
        analysis.expansion_opportunity_score
        is not None
    )


def test_missing_operational_data_has_80_percent_completeness():
    scoring = ScoringService()

    metrics = create_complete_metrics()

    metrics.delay_rate_pct = None
    metrics.cancellation_rate_pct = None

    analysis = scoring.analyze(
        metrics
    )

    assert analysis.operational_congestion_score is None

    assert analysis.data_completeness_pct == 80.0

    assert (
        analysis.expansion_opportunity_score
        is not None
    )


def test_expansion_score_is_between_zero_and_100():
    scoring = ScoringService()

    analysis = scoring.analyze(
        create_complete_metrics()
    )

    assert (
        0
        <= analysis.expansion_opportunity_score
        <= 100
    )
