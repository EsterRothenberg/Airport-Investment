"""
Tests for scoring service.
"""

import unittest
from services.scoring_service import ScoringService


class TestScoringService(unittest.TestCase):
    """Test cases for ScoringService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = ScoringService()
    
    def test_recommendation_strong_buy(self):
        """Test strong buy recommendation."""
        recommendation = self.service.generate_recommendation(8.5)
        self.assertEqual(recommendation, "STRONG BUY")
    
    def test_recommendation_buy(self):
        """Test buy recommendation."""
        recommendation = self.service.generate_recommendation(6.5)
        self.assertEqual(recommendation, "BUY")
    
    def test_recommendation_hold(self):
        """Test hold recommendation."""
        recommendation = self.service.generate_recommendation(4.5)
        self.assertEqual(recommendation, "HOLD")
    
    def test_recommendation_avoid(self):
        """Test avoid recommendation."""
        recommendation = self.service.generate_recommendation(2.0)
        self.assertEqual(recommendation, "AVOID")


if __name__ == '__main__':
    unittest.main()
