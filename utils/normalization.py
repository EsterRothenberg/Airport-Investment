"""
Data normalization utilities.
"""

from typing import Any, Dict, List


class Normalizer:
    """Utility class for data normalization."""
    
    @staticmethod
    def normalize_range(value: float, min_val: float, max_val: float) -> float:
        """Normalize a value to 0-1 range."""
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)
    
    @staticmethod
    def normalize_zero_mean(values: List[float]) -> List[float]:
        """Normalize values to zero mean."""
        if not values:
            return []
        mean = sum(values) / len(values)
        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        if std == 0:
            return [0.0] * len(values)
        return [(x - mean) / std for x in values]
    
    @staticmethod
    def normalize_dict_values(data: Dict[str, float]) -> Dict[str, float]:
        """Normalize all values in a dictionary."""
        if not data:
            return {}
        values = list(data.values())
        min_val = min(values)
        max_val = max(values)
        return {
            key: Normalizer.normalize_range(val, min_val, max_val)
            for key, val in data.items()
        }
