from datetime import datetime

import requests

from models.traffic import AirportTraffic


class BTSApiError(Exception):
    pass


class BTSApiClient:
    BASE_URL = "https://data.transportation.gov/resource/r495-tyji.json"

    def __init__(
        self,
        timeout: int = 20,
    ):
        self.timeout = timeout

        # Cache raw monthly airport traffic:
        # key = airport_code
        self._traffic_cache: dict[
            str,
            list[AirportTraffic],
        ] = {}

        # Cache annual aggregated traffic:
        # key = (airport_code, year)
        self._annual_cache: dict[
            tuple[str, int],
            AirportTraffic | None,
        ] = {}

    def get_airport_traffic(
        self,
        airport_code: str,
        year: int | None = None,
    ) -> list[AirportTraffic]:

        airport_code = (
            airport_code
            .upper()
            .strip()
        )

        # -----------------------------------------
        # 1. Load airport history only once
        # -----------------------------------------

        if airport_code not in self._traffic_cache:
            self._traffic_cache[
                airport_code
            ] = self._fetch_airport_traffic(
                airport_code
            )

        records = self._traffic_cache[
            airport_code
        ]

        # -----------------------------------------
        # 2. Optionally filter cached data by year
        # -----------------------------------------

        if year is not None:
            return [
                record
                for record in records
                if record.year == year
            ]

        return records

    def get_latest_airport_traffic(
        self,
        airport_code: str,
    ) -> AirportTraffic | None:

        records = self.get_airport_traffic(
            airport_code
        )

        if not records:
            return None

        return max(
            records,
            key=lambda record: (
                record.year,
                record.month or 0,
            ),
        )

    def get_annual_traffic(
        self,
        airport_code: str,
        year: int,
    ) -> AirportTraffic | None:

        airport_code = (
            airport_code
            .upper()
            .strip()
        )

        cache_key = (
            airport_code,
            year,
        )

        # -----------------------------------------
        # Annual aggregation cache
        # -----------------------------------------

        if cache_key in self._annual_cache:
            return self._annual_cache[
                cache_key
            ]

        records = self.get_airport_traffic(
            airport_code=airport_code,
            year=year,
        )

        if not records:
            self._annual_cache[
                cache_key
            ] = None

            return None

        passengers = sum(
            record.passengers or 0
            for record in records
        )

        seats = sum(
            record.seats or 0
            for record in records
        )

        departures = sum(
            record.departures or 0
            for record in records
        )

        load_factor = (
            passengers / seats * 100
            if seats > 0
            else None
        )

        result = AirportTraffic(
            airport_code=airport_code,
            year=year,
            month=None,

            passengers=passengers,
            seats=seats,
            departures=departures,

            load_factor_pct=(
                round(load_factor, 2)
                if load_factor is not None
                else None
            ),
        )

        self._annual_cache[
            cache_key
        ] = result

        return result

    def _fetch_airport_traffic(
        self,
        airport_code: str,
    ) -> list[AirportTraffic]:

        params = {
            "$where": (
                f"origin_airport_code="
                f"'{airport_code}'"
            ),
            "$limit": 5000,
            "$order": (
                "year ASC, "
                "reporting_month ASC"
            ),
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise BTSApiError(
                f"Failed to fetch BTS data "
                f"for {airport_code}"
            ) from exc

        rows = response.json()

        return [
            self._parse_airport_traffic(
                row
            )
            for row in rows
        ]

    @staticmethod
    def _parse_airport_traffic(
        row: dict,
    ) -> AirportTraffic:

        reporting_month = row.get(
            "reporting_month"
        )

        month = None

        if reporting_month:
            try:
                month = (
                    datetime.fromisoformat(
                        reporting_month.replace(
                            "Z",
                            "+00:00",
                        )
                    ).month
                )

            except ValueError:
                month = None

        return AirportTraffic(
            airport_code=row[
                "origin_airport_code"
            ],

            year=int(
                row["year"]
            ),

            month=month,

            passengers=(
                BTSApiClient._to_int(
                    row.get(
                        "total_passengers"
                    )
                )
            ),

            seats=(
                BTSApiClient._to_int(
                    row.get(
                        "total_seats"
                    )
                )
            ),

            departures=(
                BTSApiClient._to_int(
                    row.get(
                        "total_departures"
                    )
                )
            ),

            load_factor_pct=(
                BTSApiClient._to_float(
                    row.get(
                        "total_load_factor"
                    )
                )
            ),
        )

    @staticmethod
    def _to_int(
        value: str | int | float | None,
    ) -> int | None:

        if value in (
            None,
            "",
        ):
            return None

        return int(
            float(value)
        )

    @staticmethod
    def _to_float(
        value: str | int | float | None,
    ) -> float | None:

        if value in (
            None,
            "",
        ):
            return None

        return float(value)
