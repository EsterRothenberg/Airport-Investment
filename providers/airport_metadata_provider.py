from pathlib import Path

import pandas as pd

from models.airport import Airport


class AirportMetadataError(Exception):
    pass


class AirportMetadataProvider:
    REQUIRED_COLUMNS = {
        "type",
        "name",
        "latitude_deg",
        "longitude_deg",
        "iso_country",
        "iso_region",
        "municipality",
        "scheduled_service",
        "iata_code",
    }

    def __init__(
        self,
        data_path: str | Path,
    ):
        self.data_path = Path(data_path)
        self._data = self._load()

    def _load(
        self,
    ) -> pd.DataFrame:
        if not self.data_path.exists():
            raise AirportMetadataError(
                f"Airport metadata file not found: {self.data_path}"
            )

        df = pd.read_csv(
            self.data_path,
            low_memory=False,
        )

        missing = (
            self.REQUIRED_COLUMNS
            - set(df.columns)
        )

        if missing:
            raise AirportMetadataError(
                "Missing airport metadata columns: "
                + ", ".join(sorted(missing))
            )

        # U.S. airports only
        df = df[
            df["iso_country"] == "US"
        ].copy()

        # We need an IATA code because the rest of our
        # analytical pipeline works with IATA identifiers.
        df = df[
            df["iata_code"].notna()
        ].copy()

        df["iata_code"] = (
            df["iata_code"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df["name_normalized"] = (
            df["name"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
        )

        df["city_normalized"] = (
            df["municipality"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
        )

        df["state_code"] = (
            df["iso_region"]
            .fillna("")
            .astype(str)
            .str.replace(
                "US-",
                "",
                regex=False,
            )
            .str.upper()
        )

        return df

    def find_by_code(
        self,
        airport_code: str,
    ) -> Airport | None:
        code = (
            airport_code
            .upper()
            .strip()
        )

        matches = self._data[
            self._data["iata_code"] == code
        ]

        if matches.empty:
            return None

        return self._to_airport(
            matches.iloc[0]
        )

    def find_by_city(
        self,
        city: str,
        commercial_only: bool = True,
    ) -> list[Airport]:
        query = city.lower().strip()

        df = self._data[
            self._data["city_normalized"]
            == query
        ]

        df = self._filter_commercial(
            df,
            commercial_only,
        )

        return self._to_airports(df)

    def find_by_name(
        self,
        name_query: str,
        commercial_only: bool = True,
    ) -> list[Airport]:
        query = name_query.lower().strip()

        df = self._data[
            self._data["name_normalized"]
            .str.contains(
                query,
                regex=False,
                na=False,
            )
        ]

        df = self._filter_commercial(
            df,
            commercial_only,
        )

        return self._to_airports(df)

    def find_by_states(
        self,
        state_codes: list[str],
        commercial_only: bool = True,
    ) -> list[Airport]:
        states = {
            code.upper().strip()
            for code in state_codes
        }

        df = self._data[
            self._data["state_code"].isin(
                states
            )
        ]

        df = self._filter_commercial(
            df,
            commercial_only,
        )

        return self._to_airports(df)

    @staticmethod
    def _filter_commercial(
        df: pd.DataFrame,
        commercial_only: bool,
    ) -> pd.DataFrame:
        if not commercial_only:
            return df

        # scheduled_service is documented as yes/no.
        return df[
            df["scheduled_service"] == "yes"
        ]

    def _to_airports(
        self,
        df: pd.DataFrame,
    ) -> list[Airport]:
        return [
            self._to_airport(row)
            for _, row in df.iterrows()
        ]

    @staticmethod
    def _to_airport(
        row: pd.Series,
    ) -> Airport:
        return Airport(
            iata_code=row["iata_code"],
            name=row["name"],
            city=(
                row["municipality"]
                if pd.notna(row["municipality"])
                else None
            ),
            state_code=(
                row["state_code"]
                if row["state_code"]
                else None
            ),
            latitude=(
                float(row["latitude_deg"])
                if pd.notna(row["latitude_deg"])
                else None
            ),
            longitude=(
                float(row["longitude_deg"])
                if pd.notna(row["longitude_deg"])
                else None
            ),
            airport_type=(
                row["type"]
                if pd.notna(row["type"])
                else None
            ),
            scheduled_service=(
                row["scheduled_service"]
                == "yes"
            ),
        )
