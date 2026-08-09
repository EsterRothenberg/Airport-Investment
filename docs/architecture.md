# Airport Investment Intelligence Agent - Architecture & Design

## Executive Summary

The Airport Investment Intelligence Agent is an AI-powered system designed to help investment firms identify promising airport modernization opportunities. The system uses deterministic scoring logic combined with conversational AI to provide data-driven investment recommendations.

**Key Capability**: Answers complex queries like "Which airports in New England are strong candidates for terminal expansion?" by fetching data from multiple sources, applying multi-factor scoring logic, and explaining reasoning clearly.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Interface (CLI)                      │
│            (Natural language query → response)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│           Conversational Agent (agent.py)                    │
│  - Query parsing & intent classification                    │
│  - Multi-turn conversation context                          │
│  - Response orchestration                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
│  Data Fetching │  │   Scoring   │  │  Comparison &  │
│  (Providers)   │  │   Logic     │  │   Ranking      │
└───────┬────────┘  └──────┬──────┘  └───────┬────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼──────────┐              ┌──────────▼────────┐
│ Data Providers   │              │    Services       │
│ - BTS API        │              │ - Scoring         │
│ - FAA API        │              │ - Analytics       │
│ - T100 Provider  │              │ - Airport Mgmt    │
└──────────────────┘              └───────────────────┘
```

## Scoring Methodology

### Overview

The investment score is calculated using a **deterministic, multi-factor scoring system** (0-10 scale) that combines six equally-weighted KPI categories. This ensures transparency and reproducibility.

### Six Scoring Factors (20% weight each)

#### 1. **Traffic Growth Score** (0-10)
**What**: Year-over-year passenger growth rate
**Rationale**: Growing airports signal increased demand and revenue potential
**Calculation**:
- Score = min(10, max(0, growth_rate_percentage))
- Example: 8% growth → 8.0/10

**Why it matters**: Demonstrates market momentum and expansion viability

#### 2. **Capacity Utilization Score** (0-10)
**What**: Runway utilization percentage
**Rationale**: High utilization indicates congestion and expansion urgency
**Calculation**:
- <50% utilization → 3.0/10 (underutilized)
- 50-75% → 6.0/10 (moderate)
- 75-90% → 8.0/10 (good expansion opportunity)
- >90% → 10.0/10 (urgent expansion need)

**Why it matters**: Quantifies growth constraint and ROI urgency

#### 3. **Financial Efficiency Score** (0-10)
**What**: Airport size based on annual passenger volume
**Rationale**: Larger airports generate more revenue to support modernization
**Calculation**:
- Logarithmic scale: (log₁₀(passengers) - 6) × 2
- 10M passengers → 2/10, 100M passengers → 10/10

**Why it matters**: Revenue potential scales with airport size

#### 4. **Market Position Score** (0-10)
**What**: International connectivity (routes, airlines, seat utilization)
**Rationale**: Strong international presence increases premium pricing power
**Calculation**:
- Route score: min(10, routes/5)
- Airline score: min(10, airlines/3)
- Utilization score: seat_utilization/10
- Average of three components

**Why it matters**: International routes support higher margins on modernization ROI

#### 5. **Growth Potential Score** (0-10)
**What**: Unmet demand signals (utilization + congestion)
**Rationale**: High demand with constraints = strong expansion opportunity
**Calculation**:
- >85% utilization + HIGH congestion → 9.0/10
- 75-85% utilization → 7.5/10
- 60-75% → 6.0/10
- <60% → 4.0/10

**Why it matters**: Forward-looking indicator of expansion urgency

#### 6. **Operational Health Score** (0-10)
**What**: On-time performance and safety rating
**Rationale**: Operational excellence required for premium investments
**Calculation**:
- On-time score: OTP_percentage / 10
- Safety score: A=10, B=8, C=5
- Average of two components

**Why it matters**: Reduces operational risk in modernization projects

### Overall Score Calculation

```
Overall Score = 0.20 × (Growth Score) +
                0.20 × (Capacity Score) +
                0.20 × (Financial Score) +
                0.20 × (Market Score) +
                0.10 × (Potential Score) +
                0.10 × (Health Score)
```

### Investment Recommendations

| Score Range | Recommendation | Meaning |
|-------------|-----------------|---------|
| 8.0+ | STRONG BUY | Excellent expansion opportunity, high confidence |
| 6.5-8.0 | BUY | Good investment potential, execute with standard diligence |
| 5.0-6.5 | HOLD | Monitor for opportunities, wait for catalyst |
| 3.0-5.0 | WEAK | Limited growth indicators, avoid unless strategic |
| <3.0 | AVOID | Poor risk/reward profile |

## Key Design Tradeoffs

### 1. **Deterministic vs. AI-Driven Scoring**

**Decision**: Deterministic scoring with AI for explanation
- ✅ Reproducible and auditable
- ✅ Regulatory compliant
- ✅ Transparent to stakeholders
- ❌ May miss complex interactions
- ❌ Requires manual rule updates

**Alternative**: Pure LLM-based scoring
- ✅ Adaptive to new patterns
- ✅ Can capture complex relationships
- ❌ Black box, difficult to audit
- ❌ May have hidden biases
- ❌ Regulatory concerns

**Chosen Approach**: Deterministic scoring ensures investment decisions are defensible while LLM can provide narrative explanation and context.

### 2. **Mock Data vs. Real API Integration**

**Decision**: Mock data with real API infrastructure
- ✅ Fast development (no API keys, rate limits)
- ✅ Consistent for testing/demo
- ✅ Extensible to real APIs
- ❌ Not production-ready for real investments
- ❌ May not capture all real nuances

**For Production**: Replace providers with real API integrations:
```python
# Mock providers return deterministic data
# Real providers would call:
# - BTS TransStats API
# - FAA API  
# - Eurocontrol T100 data
# - Airport operator APIs
```

### 3. **Conversation Context vs. Stateless Queries**

**Decision**: Maintain conversation history with context
- ✅ Supports follow-up questions ("What about this airport?")
- ✅ Better user experience
- ✅ Enables multi-turn reasoning
- ❌ More complex state management
- ❌ Privacy implications with data storage

### 4. **Equal Weighting vs. Empirical Weighting**

**Decision**: Equal 20% weighting for first four factors, lower weight for speculative factors
- ✅ Simple, transparent, defensible
- ✅ Avoids overfitting to historical data
- ❌ May not reflect actual ROI drivers
- ❌ Requires expert calibration

**Alternative**: Empirical weighting based on historical ROI data
- Would require extensive backtesting
- Could be added post-MVP

## Data Integration

### Providers

#### BTS API Provider (`bts_api.py`)
**Provides**:
- Historical traffic data (12 months)
- Passenger and flight counts
- Domestic/international ratios

**Quality**: Public government data, highly reliable
**Latency**: Publicly available, no rate limits
**Coverage**: All US commercial airports

#### FAA Provider (`faa_provider.py`)
**Provides**:
- Airport infrastructure (gates, runways, terminals)
- Operational metrics (utilization, delays)
- Safety ratings

**Quality**: Authoritative FAA data
**Coverage**: All US airports

#### T100 Provider (`t100_provider.py`)
**Provides**:
- International routes and carriers
- Seat capacity and utilization
- Weekly schedule data

**Quality**: BTS T100 international airline statistics
**Coverage**: Carriers with US international routes

### Data Freshness Assumptions
- **Traffic data**: Monthly (12-month history)
- **Operational metrics**: Weekly
- **International routes**: Monthly
- **Update frequency**: Scores recalculated weekly

**Note**: Mock implementation uses random data within realistic bounds. Production version requires scheduled API sync.

## Query Processing

### Intent Classification

The agent uses pattern matching to classify queries into types:

1. **Expansion Queries** → Region analysis + ranking
   - Pattern: "terminal", "expansion", "candidate", "New England"
   - Action: Fetch all airports in region, rank by expansion potential

2. **Comparison Queries** → Pairwise analysis
   - Pattern: "compare", "vs", "congestion"
   - Action: Extract airport codes, fetch both, generate comparison

3. **Statistical Queries** → Specific metrics
   - Pattern: "percentage", "long haul", "flights"
   - Action: Fetch flight data, extract statistics

4. **Demand Queries** → Capacity analysis
   - Pattern: "unmet", "demand", "capacity"
   - Action: Analyze utilization, generate recommendations

### Response Generation

**For Deterministic Analysis**:
- Query data providers
- Calculate scores for each factor
- Explain reasoning for each score
- Generate actionable recommendations

**For Rankings**:
- Score all airports
- Sort by score
- Show top opportunities
- Explain key differentiators

**For Comparisons**:
- Score both airports
- Highlight differences
- Identify winner
- Provide reasoning

## Use of AI/LLM

### Where AI is NOT Used (Critical Decision)
❌ Scoring calculations - All deterministic
❌ Investment recommendations - Based on scores, not LLM output
❌ Risk assessment - Rule-based

### Where AI Can Be Used (Optional Enhancement)
✓ Narrative explanation of scores (LLM generates human-readable reasoning)
✓ Follow-up question understanding (LLM for NLP understanding)
✓ Report generation (LLM expands scores into prose)
✓ Uncertainty quantification (LLM writes about data gaps)

### LLM Integration Pattern (Future)

```python
# Current: Pattern matching
if "expand" in query and "new england" in query:
    handle_expansion_query()

# Future: LLM-assisted query understanding
response = llm(
    system="Extract intent, entities, and constraints from user query",
    user_query=query
)
intent = response.intent  # "expansion"
entities = response.entities  # ["New England"]
confidence = response.confidence  # 0.95
```

**Recommended LLM for this use case**:
- Claude (Anthropic) or GPT-4 for explanation quality
- Smaller models (Phi, Mistral) for cost optimization
- Open source options (Llama 2) for data privacy

**Key Constraint**: LLM output should never override deterministic scores

## Assumptions & Limitations

### Assumptions
1. **Traffic data is current** - Assumes monthly data freshness
2. **Runways are homogeneous** - Doesn't distinguish runway types (narrow vs. wide body)
3. **Linear growth extrapolation** - Assumes recent trends continue
4. **US-focused** - Data sources primarily US airports
5. **Capital-neutral analysis** - Doesn't model project costs or financing
6. **Market-efficient** - Assumes no major unpriced shocks (pandemic, strikes)

### Data Quality Issues

| Issue | Impact | Mitigation |
|-------|--------|-----------|
| Missing international data for small airports | Low market scores | Note limitations in report |
| Delay in BTS data (lag up to 3 months) | Stale trends | Use forward guidance where available |
| Construction events not captured | May miss constraints | Add construction flag to models |
| Weather/seasonal effects not modeled | Score noise | Add deseasonalization |

### Scoping Notes

**Out of Scope (v1.0)**:
- ❌ Capital expenditure estimates
- ❌ Competitive impact analysis
- ❌ Regulatory approval risk
- ❌ Environmental/climate risk
- ❌ Macro economic forecasting
- ❌ Real estate/land value analysis

**Potential v2.0 Additions**:
- 📈 Multi-year forecasting model
- 💰 ROI calculator
- 🏗️ Construction timeline modeling
- 🌍 Climate risk scoring
- 📊 Peer group comparison
- 🤖 ML model for regression testing

## Deployment Considerations

### Development Mode (Current)
- Mock data providers
- CLI chat interface
- Single-threaded execution
- No authentication

### Production Deployment
1. **API Authentication**
   - Secure storage of BTS/FAA API keys
   - OAuth for user access

2. **Scaling**
   - Async query processing
   - Caching layer for frequently requested airports
   - Background jobs for data refresh

3. **Monitoring**
   - Query latency tracking
   - Scoring anomaly detection
   - Data freshness monitoring

4. **Data Privacy**
   - Conversation history encryption
   - Audit logging for compliance
   - Data retention policies

## Testing & Validation

### Unit Tests
- `test_analytics.py` - Analytics calculations
- `test_scoring.py` - Scoring logic validation

### Integration Tests (To Add)
- End-to-end query processing
- Provider data validation
- Score reproducibility

### Validation Set
Four example queries:
1. ✅ New England expansion analysis
2. ✅ LAX vs SNA congestion comparison
3. ✅ Anchorage long-haul flight percentage
4. ✅ SFO unmet demand analysis

## Conclusion

The Airport Investment Intelligence Agent balances **transparency** (deterministic scoring), **usability** (conversational interface), and **accuracy** (multi-source data) to provide investment-grade airport analysis.

**Key Success Factors**:
- Deterministic scoring ensures defensibility
- Conversation support enables deeper analysis
- Mock data allows rapid iteration without API dependencies
- Clear separation between data, scoring, and UI layers

**Next Steps**:
1. Integrate real data sources (BTS, FAA, T100 APIs)
2. Add LLM for enhanced explanation generation
3. Implement web interface for wider adoption
4. Add historical backtesting for score validation
5. Extend to international airports

