"""
Configuration settings for the application.
"""

import os
from typing import Optional


class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        self.api_key = os.getenv('API_KEY', '')
        self.bts_api_key = os.getenv('BTS_API_KEY', '')
        self.faa_api_key = os.getenv('FAA_API_KEY', '')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def validate(self) -> bool:
        """Validate critical settings."""
        return bool(self.api_key)
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"Settings(log_level={self.log_level}, debug={self.debug})"
