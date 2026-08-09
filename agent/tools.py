"""
Tools available to the Airport Investment Agent.
"""

from typing import Any, Dict, List


class AgentTools:
    """Tools for the Airport Investment Agent."""
    
    def __init__(self):
        """Initialize agent tools."""
        pass
    
    def fetch_traffic_data(self, airport_code: str) -> Dict[str, Any]:
        """Fetch traffic data for an airport."""
        raise NotImplementedError
    
    def fetch_financial_data(self, airport_code: str) -> Dict[str, Any]:
        """Fetch financial metrics for an airport."""
        raise NotImplementedError
    
    def calculate_scoring(self, data: Dict[str, Any]) -> float:
        """Calculate investment score based on data."""
        raise NotImplementedError
