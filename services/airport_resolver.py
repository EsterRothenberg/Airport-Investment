from models.airport import Airport
from providers.airport_metadata_provider import (
    AirportMetadataProvider,
)


class AirportResolver:
    def __init__(
        self,
        metadata_provider: AirportMetadataProvider,
    ):
        self.metadata_provider = (
            metadata_provider
        )

    def resolve_code(
        self,
        airport_code: str,
    ) -> Airport | None:
        return (
            self.metadata_provider
            .find_by_code(
                airport_code
            )
        )

    def find_by_city(
        self,
        city: str,
    ) -> list[Airport]:
        return (
            self.metadata_provider
            .find_by_city(
                city=city,
                commercial_only=True,
            )
        )

    def find_by_name(
        self,
        name_query: str,
    ) -> list[Airport]:
        return (
            self.metadata_provider
            .find_by_name(
                name_query=name_query,
                commercial_only=True,
            )
        )

    def find_by_states(
        self,
        states: list[str],
    ) -> list[Airport]:
        return (
            self.metadata_provider
            .find_by_states(
                state_codes=states,
                commercial_only=True,
            )
        )
