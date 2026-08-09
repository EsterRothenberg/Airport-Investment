"""
Core agent implementation for airport investment analysis with conversational capabilities.
"""

from typing import Any, Dict, List, Optional, Tuple
from agent.prompts import AgentPrompts
from agent.tools import AgentTools
from providers.bts_api import BTSProvider
from providers.faa_provider import FAAProvider
from providers.t100_provider import T100Provider
from services.airport_service import AirportService
from services.analytics_service import AnalyticsService
from services.scoring_service import ScoringService
from models.analysis import InvestmentAnalysis
import json


class AirportInvestmentAgent:
    """AI-powered agent for analyzing airport investment opportunities."""
    
    def __init__(self, settings: Any):
        """Initialize the Airport Investment Agent."""
        self.settings = settings
        self.prompts = AgentPrompts()
        self.tools = AgentTools()
        
        # Initialize providers
        self.bts_provider = BTSProvider(settings.bts_api_key)
        self.faa_provider = FAAProvider(settings.faa_api_key)
        self.t100_provider = T100Provider()
        
        # Initialize services
        self.airport_service = AirportService()
        self.analytics_service = AnalyticsService()
        self.scoring_service = ScoringService()
        
        # Conversation history for context
        self.conversation_history = []
    
    def fetch_airport_data(self, airport_code: str) -> Dict[str, Any]:
        """Fetch comprehensive data for an airport from all providers."""
        traffic_data = self.bts_provider.get_airport_traffic(airport_code)
        ops_data = self.faa_provider.get_operational_metrics(airport_code)
        carrier_data = self.t100_provider.get_carrier_data(airport_code)
        
        return {
            'airport_code': airport_code,
            'traffic_data': traffic_data,
            'ops_data': ops_data,
            'carrier_data': carrier_data,
        }
    
    def analyze(self, airport_code: str) -> InvestmentAnalysis:
        """Analyze investment potential for a single airport."""
        data = self.fetch_airport_data(airport_code)
        
        analysis = self.scoring_service.analyze_airport(
            airport_code=airport_code,
            traffic_data=data['traffic_data'],
            ops_data=data['ops_data'],
            carrier_data=data['carrier_data']
        )
        
        return analysis
    
    def compare_airports(self, airport_codes: List[str]) -> Dict[str, Any]:
        """Compare multiple airports and rank them."""
        analyses = {}
        for code in airport_codes:
            try:
                analyses[code] = self.analyze(code)
            except Exception as e:
                print(f"Error analyzing {code}: {e}")
        
        # Sort by score
        ranked = sorted(analyses.items(), key=lambda x: x[1].score, reverse=True)
        
        return {
            'rankings': [(code, analysis.score, analysis.recommendation) 
                        for code, analysis in ranked],
            'analyses': analyses,
        }
    
    def find_airports_by_region(self, region: str) -> List[str]:
        """Find all airports in a region."""
        return self.bts_provider.list_airports_by_region(region)
    
    def analyze_region(self, region: str) -> Tuple[Dict[str, Any], List[str]]:
        """Analyze all airports in a region and rank them."""
        airport_codes = self.find_airports_by_region(region)
        if not airport_codes:
            return {}, airport_codes
        
        results = self.compare_airports(airport_codes)
        return results, airport_codes
    
    def process_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a natural language query and return analysis.
        Returns: (response_text, structured_data)
        """
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Determine query type and extract entities
        query_lower = query.lower()
        
        # Pattern matching for common query types
        if any(phrase in query_lower for phrase in ['expand', 'terminal', 'terminal expansion', 'new england']):
            return self._handle_expansion_query(query)
        
        elif any(phrase in query_lower for phrase in ['compare', 'congestion', 'vs']):
            return self._handle_comparison_query(query)
        
        elif any(phrase in query_lower for phrase in ['percentage', 'long haul', 'flights']):
            return self._handle_statistics_query(query)
        
        elif any(phrase in query_lower for phrase in ['unmet', 'demand', 'capacity']):
            return self._handle_demand_query(query)
        
        else:
            return self._handle_general_query(query)
    
    def _handle_expansion_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Handle terminal expansion recommendation queries."""
        if 'new england' in query.lower():
            results, codes = self.analyze_region('New England')
            
            if not results:
                return "No airports found in New England region.", {}
            
            response = "EXPANSION CANDIDATES - NEW ENGLAND REGION\n"
            response += "=" * 50 + "\n\n"
            
            for rank, (code, score, recommendation) in enumerate(results['rankings'], 1):
                analysis = results['analyses'][code]
                response += f"{rank}. {code} - Score: {score:.2f}/10\n"
                response += f"   Recommendation: {recommendation}\n"
                response += f"   Runway Utilization: {analysis.metrics['capacity_utilization']:.1f}/10\n"
                response += f"   Growth Potential: {analysis.metrics['growth_potential']:.1f}/10\n"
                response += f"   Top Opportunities:\n"
                for opp in analysis.opportunities[:2]:
                    response += f"     • {opp}\n"
                response += "\n"
            
            return response, results
        
        return "Could not parse expansion query. Please specify a region.", {}
    
    def _handle_comparison_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Handle airport comparison queries."""
        # Extract airport codes
        airports = []
        codes = ['LAX', 'SNA', 'SFO', 'BOS', 'MHT', 'PVD', 'BDL', 'ANC']
        
        for code in codes:
            if code in query.upper():
                airports.append(code)
        
        if len(airports) < 2:
            return "Please specify at least two airports to compare (e.g., LAX and SNA).", {}
        
        results = self.compare_airports(airports)
        
        response = "AIRPORT COMPARISON\n"
        response += "=" * 50 + "\n\n"
        
        for i, (code, analysis) in enumerate(results['analyses'].items(), 1):
            response += f"{i}. {code}\n"
            response += f"   Overall Score: {analysis.score:.2f}/10\n"
            response += f"   Recommendation: {analysis.recommendation}\n"
            response += f"   Capacity Utilization: {analysis.metrics['capacity_utilization']:.1f}/10\n"
            response += f"   On-Time Performance: {analysis.metrics['operational_health']:.1f}/10\n"
            response += f"   Congestion Level: {results.get('congestion_data', {}).get(code, 'N/A')}\n\n"
        
        # Add ranking
        response += "\nRANKING (Best to Worst):\n"
        for rank, (code, score, rec) in enumerate(results['rankings'], 1):
            response += f"{rank}. {code} - {score:.2f}/10 - {rec}\n"
        
        return response, results
    
    def _handle_statistics_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Handle statistical queries about airports."""
        # Extract airport code
        codes = ['LAX', 'SNA', 'SFO', 'BOS', 'MHT', 'PVD', 'BDL', 'ANC']
        target_airport = None
        
        for code in codes:
            if code in query.upper():
                target_airport = code
                break
        
        if not target_airport:
            return "Please specify an airport code (e.g., ANC, SFO).", {}
        
        data = self.fetch_airport_data(target_airport)
        flight_data = self.bts_provider.get_flight_data(target_airport)
        
        response = f"AIRPORT STATISTICS - {target_airport}\n"
        response += "=" * 50 + "\n\n"
        
        if 'long haul' in query.lower() or 'percentage' in query.lower():
            long_haul_pct = flight_data.get('long_haul_percentage', 0)
            response += f"Long-haul flights percentage: {long_haul_pct:.1f}%\n"
            response += f"Total flights: {flight_data.get('total_daily_flights', 0)}\n"
            response += f"Domestic flights: {flight_data.get('domestic_flights', 0)}\n"
            response += f"International flights: {flight_data.get('international_flights', 0)}\n"
            response += f"Long-haul flights: {flight_data.get('long_haul_flights', 0)}\n"
        
        return response, flight_data
    
    def _handle_demand_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Handle unmet demand and capacity queries."""
        codes = ['LAX', 'SNA', 'SFO', 'BOS', 'MHT', 'PVD', 'BDL', 'ANC']
        target_airport = None
        
        for code in codes:
            if code in query.upper():
                target_airport = code
                break
        
        if not target_airport:
            return "Please specify an airport code (e.g., SFO).", {}
        
        analysis = self.analyze(target_airport)
        data = self.fetch_airport_data(target_airport)
        
        utilization = data['ops_data'].get('runway_utilization_percentage', 0)
        slot_availability = data['ops_data'].get('slot_availability', 0)
        congestion = data['ops_data'].get('congestion_level', 'MODERATE')
        
        response = f"UNMET DEMAND ANALYSIS - {target_airport}\n"
        response += "=" * 50 + "\n\n"
        
        response += f"Current runway utilization: {utilization:.1f}%\n"
        response += f"Available capacity: {slot_availability:.1f}%\n"
        response += f"Congestion level: {congestion}\n\n"
        
        if utilization > 85:
            response += f"⚠️ CRITICAL: Airport is operating at {utilization:.1f}% capacity!\n"
            response += "Key findings:\n"
            for opp in analysis.opportunities:
                response += f"• {opp}\n"
            response += "\nExpansion recommendations:\n"
            response += f"- {analysis.recommendation}\n"
            response += "- Invest in terminal expansion to relieve congestion\n"
            response += "- Add runway capacity where possible\n"
        
        return response, analysis
    
    def _handle_general_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Handle general queries with helpful guidance."""
        response = """I can help you analyze airport investment opportunities. Try asking:

1. EXPANSION: "Which airports in New England are strong candidates for terminal expansion?"
2. COMPARISON: "Compare LA and Santa Ana airport congestion levels"
3. STATISTICS: "What is the percentage of long haul flights out of Anchorage airport?"
4. DEMAND: "What is the unmet flight demand in SFO airport and why?"

I have data for: LAX, SNA, SFO, BOS, MHT, PVD, BDL, ANC

How can I help you today?"""
        
        return response, {}
    
    def generate_report(self, airport_code: str) -> str:
        """Generate detailed investment report for an airport."""
        analysis = self.analyze(airport_code)
        return analysis.detailed_report
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """Get conversation history for context."""
        return self.conversation_history
