from pathlib import Path

import pandas as pd

from models.traffic import RouteTraffic


class T100DataError(Exception):
    pass


class T100Provider:
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)

    def get_routes(
        self,
        airport_code: str,
        year: int | None = None,
    ) -> list[RouteTraffic]:

        airport_code = airport_code.upper().strip()

        if not self.data_path.exists():
            raise T100DataError(f"T-100 data file not found: {self.data_path}")

        df = pd.read_csv(self.data_path)

        self._validate_columns(df)

        df["ORIGIN"] = df["ORIGIN"].astype(str).str.upper()
        df["DEST"] = df["DEST"].astype(str).str.upper()

        filtered = df[df["ORIGIN"] == airport_code].copy()

        if year is not None:
            filtered = filtered[filtered["YEAR"] == year]

        filtered = filtered[
            (filtered["DEPARTURES_PERFORMED"] > 0)
            & (filtered["SEATS"] > 0)
            & (filtered["ORIGIN"] != filtered["DEST"])
        ]

        if filtered.empty:
            return []

        grouped = filtered.groupby(
            ["ORIGIN", "DEST", "YEAR"],
            as_index=False,
        ).agg(
            {
                "DISTANCE": "first",
                "PASSENGERS": "sum",
                "SEATS": "sum",
                "DEPARTURES_PERFORMED": "sum",
            }
        )

        routes: list[RouteTraffic] = []

        for _, row in grouped.iterrows():
            routes.append(
                RouteTraffic(
                    origin=row["ORIGIN"],
                    destination=row["DEST"],
                    year=int(row["YEAR"]),
                    distance_miles=self._to_float(row["DISTANCE"]),
                    passengers=self._to_int(row["PASSENGERS"]),
                    seats=self._to_int(row["SEATS"]),
                    departures=self._to_int(row["DEPARTURES_PERFORMED"]),
                )
            )

        return routes

    @staticmethod
    def _validate_columns(df: pd.DataFrame) -> None:
        required = {
            "ORIGIN",
            "DEST",
            "YEAR",
            "DISTANCE",
            "PASSENGERS",
            "SEATS",
            "DEPARTURES_PERFORMED",
        }

        missing = required - set(df.columns)

        if missing:
            raise T100DataError(
                "Missing required T-100 columns: " + ", ".join(sorted(missing))
            )

    @staticmethod
    def _to_int(value) -> int | None:
        if pd.isna(value):
            return None

        return int(value)

    @staticmethod
    def _to_float(value) -> float | None:
        if pd.isna(value):
            return None

        return float(value)
