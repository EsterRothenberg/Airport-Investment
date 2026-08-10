from models.metrics import AirportMetrics
from models.analysis import AirportAnalysis


class ScoringService:
    DEMAND_WEIGHT = 0.30
    CAPACITY_WEIGHT = 0.25
    OPERATIONAL_WEIGHT = 0.20
    NETWORK_WEIGHT = 0.15
    MARKET_SCALE_WEIGHT = 0.10

    @staticmethod
    def normalize(
        value: float | int | None,
        low: float,
        high: float,
    ) -> float | None:
        if value is None:
            return None

        if high <= low:
            raise ValueError("high must be greater than low")

        normalized = (
            (float(value) - low)
            / (high - low)
            * 100
        )

        return round(
            max(
                0.0,
                min(
                    100.0,
                    normalized,
                ),
            ),
            2,
        )

    def calculate_demand_growth_score(
        self,
        metrics: AirportMetrics,
    ) -> float | None:

        passenger_growth_score = self.normalize(
            metrics.passenger_growth_pct,
            low=-5,
            high=15,
        )

        flight_growth_score = self.normalize(
            metrics.flight_growth_pct,
            low=-5,
            high=15,
        )

        return self._weighted_average(
            [
                (
                    passenger_growth_score,
                    0.60,
                ),
                (
                    flight_growth_score,
                    0.40,
                ),
            ]
        )

    def calculate_capacity_pressure_score(
        self,
        metrics: AirportMetrics,
    ) -> float | None:

        load_factor_score = self.normalize(
            metrics.load_factor_pct,
            low=60,
            high=90,
        )

        flight_growth_score = self.normalize(
            metrics.flight_growth_pct,
            low=-5,
            high=15,
        )

        return self._weighted_average(
            [
                (
                    load_factor_score,
                    0.70,
                ),
                (
                    flight_growth_score,
                    0.30,
                ),
            ]
        )

    def calculate_operational_pressure_score(
        self,
        metrics: AirportMetrics,
    ) -> float | None:

        delay_score = self.normalize(
            metrics.delay_rate_pct,
            low=5,
            high=30,
        )

        cancellation_score = self.normalize(
            metrics.cancellation_rate_pct,
            low=0,
            high=5,
        )

        return self._weighted_average(
            [
                (
                    delay_score,
                    0.75,
                ),
                (
                    cancellation_score,
                    0.25,
                ),
            ]
        )

    def calculate_network_value_score(
        self,
        metrics: AirportMetrics,
    ) -> float | None:

        route_count_score = self.normalize(
            metrics.route_count,
            low=10,
            high=150,
        )

        long_haul_score = self.normalize(
            metrics.long_haul_share_pct,
            low=0,
            high=20,
        )

        return self._weighted_average(
            [
                (
                    route_count_score,
                    0.60,
                ),
                (
                    long_haul_score,
                    0.40,
                ),
            ]
        )

    def calculate_market_scale_score(
        self,
        metrics: AirportMetrics,
    ) -> float | None:

        passenger_scale_score = self.normalize(
            metrics.passenger_volume,
            low=500_000,
            high=30_000_000,
        )

        departure_scale_score = self.normalize(
            metrics.departures,
            low=5_000,
            high=200_000,
        )

        return self._weighted_average(
            [
                (
                    passenger_scale_score,
                    0.70,
                ),
                (
                    departure_scale_score,
                    0.30,
                ),
            ]
        )

    def analyze(
        self,
        metrics: AirportMetrics,
    ) -> AirportAnalysis:

        demand_score = (
            self.calculate_demand_growth_score(
                metrics
            )
        )

        capacity_score = (
            self.calculate_capacity_pressure_score(
                metrics
            )
        )

        operational_score = (
            self.calculate_operational_pressure_score(
                metrics
            )
        )

        network_score = (
            self.calculate_network_value_score(
                metrics
            )
        )

        market_scale_score = (
            self.calculate_market_scale_score(
                metrics
            )
        )

        components = [
            (demand_score, self.DEMAND_WEIGHT),
            (capacity_score, self.CAPACITY_WEIGHT),
            (operational_score, self.OPERATIONAL_WEIGHT),
            (network_score, self.NETWORK_WEIGHT),
            (market_scale_score, self.MARKET_SCALE_WEIGHT),
        ]

        available_weight = sum(
            weight
            for score, weight in components
            if score is not None
        )

        total_weight = sum(
            weight
            for _, weight in components
        )

        data_completeness_pct = round(
            available_weight / total_weight * 100,
            2,
        )

        expansion_score = self._weighted_average(
            [
                (
                    demand_score,
                    self.DEMAND_WEIGHT,
                ),
                (
                    capacity_score,
                    self.CAPACITY_WEIGHT,
                ),
                (
                    operational_score,
                    self.OPERATIONAL_WEIGHT,
                ),
                (
                    network_score,
                    self.NETWORK_WEIGHT,
                ),
                (
                    market_scale_score,
                    self.MARKET_SCALE_WEIGHT,
                ),
            ]
        )

        assumptions = list(
            metrics.assumptions
        )

        assumptions.append(
            "Market Scale Score is based on passenger volume "
            "and annual departures and is used to reduce the risk "
            "of over-ranking very small airports with unusually high "
            "percentage growth."
        )

        return AirportAnalysis(
            airport_code=metrics.airport_code,
            demand_growth_score=demand_score,
            capacity_pressure_score=capacity_score,
            operational_congestion_score=operational_score,
            network_value_score=network_score,
            market_scale_score=market_scale_score,
            expansion_opportunity_score=expansion_score,
            data_completeness_pct=data_completeness_pct,
            assumptions=self._unique(
                assumptions
            ),
            missing_data=list(
                metrics.missing_data
            ),
        )

    @staticmethod
    def _weighted_average(
        values: list[
            tuple[
                float | None,
                float,
            ]
        ],
    ) -> float | None:

        available = [
            (
                value,
                weight,
            )
            for value, weight in values
            if value is not None
        ]

        if not available:
            return None

        total_weight = sum(
            weight
            for _, weight in available
        )

        if total_weight <= 0:
            return None

        result = sum(
            value * weight
            for value, weight in available
        ) / total_weight

        return round(
            result,
            2,
        )

    @staticmethod
    def _unique(
        values: list[str],
    ) -> list[str]:

        return list(
            dict.fromkeys(
                values
            )
        )
