from models.metrics import AirportMetrics
from models.traffic import AirportTraffic, RouteTraffic


LONG_HAUL_THRESHOLD_MILES = 3000


class AnalyticsService:
    def calculate_metrics(
        self,
        current: AirportTraffic,
        previous: AirportTraffic | None = None,
        routes: list[RouteTraffic] | None = None,
    ) -> AirportMetrics:

        assumptions: list[str] = []
        missing_data: list[str] = []

        passenger_growth = None
        flight_growth = None
        long_haul_share = None
        route_count = None

        if previous:
            passenger_growth = self.calculate_growth(
                current.passengers,
                previous.passengers,
            )

            flight_growth = self.calculate_growth(
                current.departures,
                previous.departures,
            )
        else:
            missing_data.extend(
                [
                    "passenger_growth_pct",
                    "flight_growth_pct",
                ]
            )

        load_factor = self.calculate_load_factor(
            current.passengers,
            current.seats,
        )

        if load_factor is None:
            missing_data.append("load_factor_pct")

        if routes:
            long_haul_share = self.calculate_long_haul_share(
                routes
            )

            route_count = len(
                {
                    route.destination
                    for route in routes
                    if route.destination
                }
            )

            assumptions.append(
                "Long-haul routes are defined as nonstop segments "
                f"of at least {LONG_HAUL_THRESHOLD_MILES:,} miles."
            )

        else:
            missing_data.extend(
                [
                    "long_haul_share_pct",
                    "route_count",
                ]
            )

        return AirportMetrics(
            airport_code=current.airport_code,

            passenger_volume=current.passengers,
            passenger_growth_pct=passenger_growth,

            departures=current.departures,
            flight_growth_pct=flight_growth,

            load_factor_pct=load_factor,
            long_haul_share_pct=long_haul_share,

            route_count=route_count,

            assumptions=assumptions,
            missing_data=missing_data,
            data_sources=["U.S. DOT/BTS T-100"],
        )

    @staticmethod
    def calculate_growth(
        current: int | None,
        previous: int | None,
    ) -> float | None:
        if (
            current is None
            or previous is None
            or previous <= 0
        ):
            return None

        return round(
            (current - previous)
            / previous
            * 100,
            2,
        )

    @staticmethod
    def calculate_load_factor(
        passengers: int | None,
        seats: int | None,
    ) -> float | None:
        if (
            passengers is None
            or seats is None
            or seats <= 0
        ):
            return None

        return round(
            passengers / seats * 100,
            2,
        )

    @staticmethod
    def calculate_long_haul_share(
        routes: list[RouteTraffic],
    ) -> float | None:
        valid_routes = [
            route
            for route in routes
            if (
                route.departures is not None
                and route.departures > 0
                and route.distance_miles is not None
            )
        ]

        if not valid_routes:
            return None

        total_departures = sum(
            route.departures
            for route in valid_routes
        )

        long_haul_departures = sum(
            route.departures
            for route in valid_routes
            if route.distance_miles
            >= LONG_HAUL_THRESHOLD_MILES
        )

        if total_departures <= 0:
            return None

        return round(
            long_haul_departures
            / total_departures
            * 100,
            2,
        )
