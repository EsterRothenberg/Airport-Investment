from pathlib import Path

import pandas as pd

from models.operations import AirportOperations


class OnTimeDataError(Exception):
    pass


class OnTimeProvider:
    REQUIRED_COLUMNS = {
        "YEAR",
        "MONTH",
        "ORIGIN",
        "ARR_DELAY",
        "CANCELLED",
    }

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self._cache: dict[int, pd.DataFrame] = {}

    def get_airport_operations(
        self,
        airport_code: str,
        year: int,
    ) -> AirportOperations | None:

        if not self.data_dir.exists():
            raise OnTimeDataError(
                f"On-Time data directory not found: {self.data_dir}"
            )

        combined = self._load_year(year)

        airport_code = airport_code.upper().strip()

        filtered = combined[
            (combined["ORIGIN"] == airport_code)
            & (combined["YEAR"] == year)
        ].copy()

        if filtered.empty:
            return None

        scheduled_flights = len(filtered)

        cancelled_mask = filtered["CANCELLED"] == 1

        cancelled_flights = int(
            cancelled_mask.sum()
        )

        completed = filtered[
            ~cancelled_mask
        ]

        completed_flights = len(completed)

        delayed_flights = int(
            (
                completed["ARR_DELAY"] >= 15
            ).sum()
        )

        delay_rate = (
            delayed_flights
            / completed_flights
            * 100
            if completed_flights > 0
            else None
        )

        cancellation_rate = (
            cancelled_flights
            / scheduled_flights
            * 100
            if scheduled_flights > 0
            else None
        )

        months_found = sorted(
            filtered["MONTH"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        assumptions = [
            "A delayed flight is defined as a completed flight "
            "with an arrival delay of at least 15 minutes.",
            "Delay rate excludes cancelled flights.",
            "Cancellation rate is calculated across all scheduled flights.",
        ]

        if len(months_found) < 12:
            assumptions.append(
                f"On-Time analysis is based on {len(months_found)} "
                f"months available for {year}: {months_found}."
            )

        return AirportOperations(
            airport_code=airport_code,
            year=year,
            month=None,

            scheduled_flights=scheduled_flights,
            completed_flights=completed_flights,
            delayed_flights=delayed_flights,
            cancelled_flights=cancelled_flights,

            delay_rate_pct=(
                round(delay_rate, 2)
                if delay_rate is not None
                else None
            ),

            cancellation_rate_pct=(
                round(cancellation_rate, 2)
                if cancellation_rate is not None
                else None
            ),

            assumptions=assumptions,
        )

    def _load_year(
        self,
        year: int,
    ) -> pd.DataFrame:

        if year in self._cache:
            return self._cache[year]

        files = sorted(
            self.data_dir.glob(f"{year}-*.csv")
        )

        if not files:
            raise OnTimeDataError(
                f"No On-Time files found for year {year}"
            )

        frames = []

        for file in files:
            df = pd.read_csv(file)
            self._validate_columns(df)
            frames.append(df)

        combined = pd.concat(
            frames,
            ignore_index=True,
        )

        combined["ORIGIN"] = (
            combined["ORIGIN"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        self._cache[year] = combined

        return combined

    @classmethod
    def _validate_columns(
        cls,
        df: pd.DataFrame,
    ) -> None:
        missing = cls.REQUIRED_COLUMNS - set(df.columns)

        if missing:
            raise OnTimeDataError(
                "Missing required On-Time columns: " + ", ".join(sorted(missing))
            )
