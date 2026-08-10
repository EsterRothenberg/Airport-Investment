from pathlib import Path

from models.metrics import AirportMetrics
from providers.bts_api import BTSApiClient
from providers.on_time_provider import OnTimeProvider
from providers.t100_provider import T100Provider
from services.analytics_service import AnalyticsService


class AirportDataError(Exception):
    pass


class AirportService:
    def __init__(
        self,
        t100_data_path: str | Path,
        on_time_data_dir: str | Path,
        bts_client: BTSApiClient | None = None,
        analytics_service: AnalyticsService | None = None,
    ):
        self.bts_client = bts_client or BTSApiClient()

        self.t100_provider = T100Provider(
            t100_data_path
        )

        self.on_time_provider = OnTimeProvider(
            on_time_data_dir
        )

        self.analytics_service = (
            analytics_service
            or AnalyticsService()
        )

    def get_metrics(
        self,
        airport_code: str,
        year: int,
    ) -> AirportMetrics:
        airport_code = (
            airport_code
            .upper()
            .strip()
        )

        previous_year = year - 1

        # -------------------------------------------------
        # 1. Airport-level traffic
        # -------------------------------------------------

        current_traffic = (
            self.bts_client.get_annual_traffic(
                airport_code=airport_code,
                year=year,
            )
        )

        if current_traffic is None:
            raise AirportDataError(
                f"No BTS traffic data found for "
                f"{airport_code} in {year}"
            )

        previous_traffic = (
            self.bts_client.get_annual_traffic(
                airport_code=airport_code,
                year=previous_year,
            )
        )

        # -------------------------------------------------
        # 2. Route-level T-100 data
        # -------------------------------------------------

        routes = self.t100_provider.get_routes(
            airport_code=airport_code,
            year=year,
        )

        # -------------------------------------------------
        # 3. Calculate base analytics
        # -------------------------------------------------

        metrics = (
            self.analytics_service.calculate_metrics(
                current=current_traffic,
                previous=previous_traffic,
                routes=routes,
            )
        )

        # -------------------------------------------------
        # 4. On-Time / operational data
        # -------------------------------------------------

        operations = (
            self.on_time_provider
            .get_airport_operations(
                airport_code=airport_code,
                year=year,
            )
        )

        assumptions = list(
            metrics.assumptions
        )

        missing_data = list(
            metrics.missing_data
        )

        data_sources = list(
            metrics.data_sources
        )

        delay_rate_pct = None
        cancellation_rate_pct = None

        if operations is not None:
            delay_rate_pct = (
                operations.delay_rate_pct
            )

            cancellation_rate_pct = (
                operations.cancellation_rate_pct
            )

            assumptions.extend(
                operations.assumptions
            )

            data_sources.append(
                "BTS Reporting Carrier "
                "On-Time Performance"
            )

        else:
            missing_data.extend(
                [
                    "delay_rate_pct",
                    "cancellation_rate_pct",
                ]
            )

        # -------------------------------------------------
        # 5. Return one unified AirportMetrics object
        # -------------------------------------------------

        return metrics.model_copy(
            update={
                "delay_rate_pct": delay_rate_pct,
                "cancellation_rate_pct":
                    cancellation_rate_pct,

                "assumptions":
                    self._unique(assumptions),

                "missing_data":
                    self._unique(missing_data),

                "data_sources":
                    self._unique(data_sources),
            }
        )

    @staticmethod
    def _unique(
        values: list[str],
    ) -> list[str]:
        return list(
            dict.fromkeys(values)
        )
