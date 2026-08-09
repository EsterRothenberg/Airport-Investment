"""
Prompts and prompt templates for the Airport Investment Agent.
"""


class AgentPrompts:
    """Collection of prompts for the agent."""
    
    SYSTEM_PROMPT = """You are an expert airport investment analyst AI assistant. Your role is to help 
    investment firms identify promising airport modernization opportunities based on:
    - Traffic patterns and growth trends
    - Runway/gate utilization and capacity constraints
    - Financial performance indicators
    - Market position and competitive landscape
    - Safety and operational efficiency records
    
    Always:
    - Base recommendations on deterministic scoring logic (0-10 scale)
    - Clearly explain your reasoning with specific metrics
    - Acknowledge assumptions and data limitations
    - Provide actionable insights for investment decisions
    - Support follow-up questions with context from previous answers
    """
    
    ANALYSIS_PROMPT = """Analyze the investment potential of {airport_code} based on the provided metrics:
    
    Traffic Growth Score: {growth_score:.1f}/10
    Capacity Utilization Score: {capacity_score:.1f}/10
    Financial Efficiency Score: {financial_score:.1f}/10
    Market Position Score: {market_score:.1f}/10
    Growth Potential Score: {potential_score:.1f}/10
    Operational Health Score: {health_score:.1f}/10
    
    Overall Investment Score: {overall_score:.2f}/10
    
    Provide:
    1. Your recommendation (STRONG BUY / BUY / HOLD / WEAK / AVOID)
    2. Top 3 investment strengths
    3. Top 3 risk factors
    4. Specific expansion recommendations
    5. Expected ROI timeframe
    """
    
    COMPARISON_PROMPT = """Compare {airport1} and {airport2} for investment potential:
    
    {airport1}: {score1:.2f}/10 - {metric1}
    {airport2}: {score2:.2f}/10 - {metric2}
    
    Provide:
    1. Which airport is a better investment and why
    2. Key differentiation factors
    3. Timeline for expansion at each airport
    """
    
    RANKING_PROMPT = """Rank these airports by investment potential:
    {airports_data}
    
    Provide:
    1. Clear ranking with scores
    2. Investment thesis for top 3 airports
    3. Regions with highest opportunity concentration
    """
    
    def get_analysis_prompt(self) -> str:
        """Get the analysis prompt template."""
        return self.ANALYSIS_PROMPT
    
    def get_report_prompt(self) -> str:
        """Get the report generation prompt template."""
        return self.ANALYSIS_PROMPT
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return self.SYSTEM_PROMPT
