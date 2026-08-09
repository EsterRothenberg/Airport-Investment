"""
Tests for analytics service.
"""

import unittest
from datetime import datetime
from models.traffic import TrafficMetric
from services.analytics_service import AnalyticsService


class TestAnalyticsService(unittest.TestCase):
    """Test cases for AnalyticsService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = AnalyticsService()
    
    def test_add_traffic_metric(self):
        """Test adding traffic metrics."""
        metric = TrafficMetric(
            timestamp=datetime.now(),
            passengers=100000,
            flights=500
        )
        self.service.add_traffic_metric("LAX", metric)
        self.assertIn("LAX", self.service.traffic_data)
        self.assertEqual(len(self.service.traffic_data["LAX"]), 1)
    
    def test_multiple_airports(self):
        """Test handling multiple airports."""
        metric1 = TrafficMetric(timestamp=datetime.now(), passengers=100000, flights=500)
        metric2 = TrafficMetric(timestamp=datetime.now(), passengers=150000, flights=600)
        
        self.service.add_traffic_metric("LAX", metric1)
        self.service.add_traffic_metric("JFK", metric2)
        
        self.assertEqual(len(self.service.traffic_data), 2)


if __name__ == '__main__':
    unittest.main()
