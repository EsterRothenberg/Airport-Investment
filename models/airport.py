"""
Airport data models.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Airport:
    """Represents an airport with basic information."""
    
    code: str
    name: str
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.code} - {self.name}"
