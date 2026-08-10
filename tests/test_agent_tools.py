from agent.tools import (
    get_long_haul_analysis,
)


def test_anchorage_long_haul_analysis():
    result = get_long_haul_analysis(
        "ANC"
    )

    assert result["airport_code"] == "ANC"

    assert result["total_departures"] > 0

    assert result["long_haul_departures"] >= 0

    assert (
        0
        <= result["long_haul_share_pct"]
        <= 100
    )

    expected_share = round(
        result["long_haul_departures"]
        / result["total_departures"]
        * 100,
        2,
    )

    assert (
        result["long_haul_share_pct"]
        == expected_share
    )
