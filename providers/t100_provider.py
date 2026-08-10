from pathlib import Path

import pandas as pd

from models.traffic import RouteTraffic


class T100DataError(Exception):
    pass


class T100Provider:
    REQUIRED_COLUMNS = {
        "ORIGIN",
        "DEST",
        "YEAR",
        "DISTANCE",
        "PASSENGERS",
        "SEATS",
        "DEPARTURES_PERFORMED",
    }

    def __init__(
        self,
        data_path: str | Path,
    ):
        self.data_path = Path(
            data_path
        )

        # Full T-100 CSV cache
        self._data: pd.DataFrame | None = None

        # Per-airport processed route cache
        # key = (airport_code, year)
        self._routes_cache: dict[
            tuple[str, int | None],
            list[RouteTraffic],
        ] = {}

    def get_routes(
        self,
        airport_code: str,
        year: int | None = None,
    ) -> list[RouteTraffic]:

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
        # Return processed routes from cache
        # -----------------------------------------

        if cache_key in self._routes_cache:
            return self._routes_cache[
                cache_key
            ]

        df = self._load_data()

        # -----------------------------------------
        # Filter airport
        # -----------------------------------------

        filtered = df[
            df["ORIGIN"]
            == airport_code
        ]

        if year is not None:
            filtered = filtered[
                filtered["YEAR"]
                == year
            ]

        # Only actual passenger-service departures
        filtered = filtered[
            (
                filtered[
                    "DEPARTURES_PERFORMED"
                ] > 0
            )
            & (
                filtered["SEATS"] > 0
            )
            & (
                filtered["ORIGIN"]
                != filtered["DEST"]
            )
        ].copy()

        if filtered.empty:
            self._routes_cache[
                cache_key
            ] = []

            return []

        # -----------------------------------------
        # Aggregate airline-level rows
        # into one route
        # -----------------------------------------

        grouped = (
            filtered
            .groupby(
                [
                    "ORIGIN",
                    "DEST",
                    "YEAR",
                ],
                as_index=False,
            )
            .agg(
                {
                    "DISTANCE": "first",
                    "PASSENGERS": "sum",
                    "SEATS": "sum",
                    "DEPARTURES_PERFORMED":
                        "sum",
                }
            )
        )

        routes: list[
            RouteTraffic
        ] = []

        for _, row in grouped.iterrows():
            routes.append(
                RouteTraffic(
                    origin=row[
                        "ORIGIN"
                    ],

                    destination=row[
                        "DEST"
                    ],

                    year=int(
                        row["YEAR"]
                    ),

                    month=None,

                    distance_miles=(
                        self._to_float(
                            row[
                                "DISTANCE"
                            ]
                        )
                    ),

                    passengers=(
                        self._to_int(
                            row[
                                "PASSENGERS"
                            ]
                        )
                    ),

                    seats=(
                        self._to_int(
                            row[
                                "SEATS"
                            ]
                        )
                    ),

                    departures=(
                        self._to_int(
                            row[
                                "DEPARTURES_PERFORMED"
                            ]
                        )
                    ),
                )
            )

        self._routes_cache[
            cache_key
        ] = routes

        return routes

    def _load_data(
        self,
    ) -> pd.DataFrame:

        # -----------------------------------------
        # Read the large CSV once
        # -----------------------------------------

        if self._data is not None:
            return self._data

        if not self.data_path.exists():
            raise T100DataError(
                f"T-100 data file not found: "
                f"{self.data_path}"
            )

        df = pd.read_csv(
            self.data_path,
            usecols=list(
                self.REQUIRED_COLUMNS
            ),
            low_memory=False,
        )

        self._validate_columns(
            df
        )

        # -----------------------------------------
        # Normalize once
        # -----------------------------------------

        df["ORIGIN"] = (
            df["ORIGIN"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df["DEST"] = (
            df["DEST"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # Convert relevant numeric columns once
        numeric_columns = [
            "YEAR",
            "DISTANCE",
            "PASSENGERS",
            "SEATS",
            "DEPARTURES_PERFORMED",
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        self._data = df

        return self._data

    @classmethod
    def _validate_columns(
        cls,
        df: pd.DataFrame,
    ) -> None:

        missing = (
            cls.REQUIRED_COLUMNS
            - set(df.columns)
        )

        if missing:
            raise T100DataError(
                "Missing required T-100 columns: "
                + ", ".join(
                    sorted(missing)
                )
            )

    @staticmethod
    def _to_int(
        value,
    ) -> int | None:

        if pd.isna(value):
            return None

        return int(value)

    @staticmethod
    def _to_float(
        value,
    ) -> float | None:

        if pd.isna(value):
            return None

        return float(value)
