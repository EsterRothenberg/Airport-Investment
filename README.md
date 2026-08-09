# Airport Investment Intelligence Agent

A sophisticated AI-powered agent for analyzing airport investment opportunities. Identifies promising terminal expansion candidates using data-driven scoring and conversational analysis.

**Timeframe**: Achievable in ~1 day | **Status**: MVP Complete ✅

## Quick Start

### Installation

```bash
# Clone and setup
cd airport-investment-agent
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Agent

```bash
python app.py
```

You'll see an interactive chat interface where you can ask questions about airports.

## Example Queries

Try asking:

```
Which airports in New England are strong candidates for terminal expansion?
Compare LA and Santa Ana airport congestion levels
What is the percentage of long haul flights out of Anchorage airport?
What is the unmet flight demand in SFO airport and why?
```

## Features

### 🎯 Key Capabilities

- **Multi-source Data Integration**: Combines BTS, FAA, and T100 airline data
- **Deterministic Scoring**: 6-factor investment scoring system (0-10 scale)
- **Conversational Interface**: Natural language queries with follow-up support
- **Comparative Analysis**: Rank and compare airports by investment potential
- **Transparent Reasoning**: Detailed explanation of scores and recommendations
- **Regional Analysis**: Find best opportunities in geographic regions

### 📊 Scoring Factors (Equal Weight)

1. **Traffic Growth** - Year-over-year passenger growth rate
2. **Capacity Utilization** - Runway utilization and congestion levels
3. **Financial Efficiency** - Airport size and revenue potential
4. **Market Position** - International connectivity and routes
5. **Growth Potential** - Unmet demand indicators
6. **Operational Health** - On-time performance and safety

### 📈 Investment Recommendations

| Score | Recommendation | Interpretation |
|-------|-----------------|---|
| 8.0+ | **STRONG BUY** | Excellent expansion opportunity |
| 6.5-8.0 | **BUY** | Good investment potential |
| 5.0-6.5 | **HOLD** | Monitor for opportunities |
| <5.0 | **WEAK/AVOID** | Limited growth signals |

## Supported Airports

**New England**: BOS (Boston), MHT (Manchester), PVD (Providence), BDL (Hartford)
**California**: LAX (LA), SNA (Santa Ana), SFO (San Francisco)
**Alaska**: ANC (Anchorage)

## Usage Examples

### Interactive Chat
```bash
$ python app.py

You: Which New England airports are good expansion candidates?
Agent: EXPANSION CANDIDATES - NEW ENGLAND REGION
========================================================

1. BOS - Score: 7.54/10
   Recommendation: BUY - Good investment potential
   Runway Utilization: 7.5/10
   Growth Potential: 7.2/10
   ...
```

### Programmatic Usage
```python
from agent.agent import AirportInvestmentAgent
from config.settings import Settings

agent = AirportInvestmentAgent(Settings())

# Single airport analysis
analysis = agent.analyze("LAX")
print(analysis.recommendation)  # "STRONG BUY - Excellent expansion opportunity"

# Compare multiple airports
results = agent.compare_airports(["LAX", "SNA", "SFO"])
print(results['rankings'])  # Ranked by investment score

# Natural language query
response, data = agent.process_query("Compare LAX and SNA congestion")
print(response)
```

## Architecture

### High-Level Flow
```
User Query (Chat Interface)
        ↓
Query Classification (Intent Detection)
        ↓
Data Fetching (BTS, FAA, T100 Providers)
        ↓
Scoring Logic (6-Factor Deterministic Model)
        ↓
Ranking/Comparison
        ↓
Response Generation with Reasoning
```

### Key Modules

**`agent/`** - Agent logic and chat interface
- `agent.py` - Core analysis engine
- `chat.py` - Interactive chat interface
- `prompts.py` - Prompt templates

**`providers/`** - Data sources (currently mock, extensible to real APIs)
- `bts_api.py` - Traffic and passenger data
- `faa_provider.py` - Operational metrics
- `t100_provider.py` - International airline data

**`services/`** - Business logic
- `scoring_service.py` - Investment scoring (6 factors)
- `analytics_service.py` - Data aggregation
- `airport_service.py` - Airport management

**`models/`** - Data structures
- `airport.py`, `traffic.py`, `metrics.py`, `analysis.py`

## Design Highlights

### 1. Deterministic Scoring (Not Just LLM)
✅ **Why**: Ensures transparency, auditability, and regulatory compliance
- All scores calculated with deterministic logic
- Every recommendation backed by specific metrics
- Scores 100% reproducible across runs

### 2. Mock Data + Extensible Architecture
✅ **Why**: Enables rapid development without external dependencies
- Providers use realistic mock data
- Easy to swap for real APIs (BTS, FAA, T100)
- No API keys required for demo

### 3. Conversational Agent
✅ **Why**: Supports complex analysis through multi-turn interaction
- Maintains conversation history
- Handles regional analysis, comparisons, statistics
- Follows up with relevant context

### 4. Balanced Scoring Weights
Equal 20% weight for core factors:
- Growth + Utilization + Financial + Market factors equally important
- Growth Potential and Health at 10% each (forward-looking, less speculative)

## Key Assumptions & Limitations

### Assumptions
- ✓ Traffic data is current (monthly cadence)
- ✓ Runway capacity is homogeneous (doesn't model runway mix)
- ✓ Linear growth extrapolation
- ✓ US-focused analysis (data sources primarily US)
- ✓ Capital-neutral (doesn't model project costs)

### Out of Scope (v1.0)
- ❌ Capital expenditure estimates
- ❌ Financing/ROI models
- ❌ Regulatory approval risk
- ❌ Environmental/climate risk
- ❌ Competitive impact
- ❌ International airports

### Enhancements for v2.0
- 📈 Multi-year forecasting
- 💰 ROI calculator
- 🌍 Climate risk scoring
- 📊 Peer benchmarking
- 🤖 ML regression model validation

## Testing

```bash
# Run existing tests
python -m pytest tests/

# Test specific functionality
python -m pytest tests/test_scoring.py -v
python -m pytest tests/test_analytics.py -v
```

### Manual Test Cases

```python
# Test 1: New England expansion analysis
from agent.agent import AirportInvestmentAgent
from config.settings import Settings

agent = AirportInvestmentAgent(Settings())
results, codes = agent.analyze_region('New England')
assert len(codes) > 0
assert 'BOS' in codes

# Test 2: Score reproducibility
analysis1 = agent.analyze('LAX')
analysis2 = agent.analyze('LAX')
assert analysis1.score == analysis2.score  # Same score on identical data

# Test 3: Ranking consistency
rankings1 = agent.compare_airports(['LAX', 'SNA', 'SFO'])
rankings2 = agent.compare_airports(['LAX', 'SNA', 'SFO'])
assert rankings1['rankings'] == rankings2['rankings']
```

## Project Structure

```
airport-investment-agent/
├── app.py                      # Entry point
├── agent/
│   ├── agent.py               # Core analysis engine
│   ├── chat.py                # Chat interface
│   ├── prompts.py             # Prompt templates
│   └── tools.py               # Agent tools
├── models/
│   ├── airport.py             # Airport model
│   ├── traffic.py             # Traffic metrics
│   ├── metrics.py             # Financial metrics
│   └── analysis.py            # Analysis results
├── providers/
│   ├── bts_api.py             # BTS data (mock)
│   ├── faa_provider.py        # FAA data (mock)
│   └── t100_provider.py       # T100 data (mock)
├── services/
│   ├── scoring_service.py     # Investment scoring
│   ├── analytics_service.py   # Data aggregation
│   └── airport_service.py     # Airport management
├── config/
│   └── settings.py            # Configuration
├── utils/
│   └── normalization.py       # Data normalization
├── tests/
│   ├── test_analytics.py
│   └── test_scoring.py
├── docs/
│   └── architecture.md        # Detailed design doc
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# API Keys (not needed for mock demo)
API_KEY=your_api_key_here
BTS_API_KEY=your_bts_api_key_here
FAA_API_KEY=your_faa_api_key_here

# Application Settings
LOG_LEVEL=INFO
DEBUG=False
```

## Architecture Document

See [ARCHITECTURE.md](docs/architecture.md) for:
- Detailed scoring methodology
- Key design tradeoffs
- Data integration strategy
- Where/how AI is used
- Deployment considerations
- Validation approach

## Command Reference

**In the chat interface:**
- `help` - Show available commands
- `report [CODE]` - Generate detailed report (e.g., `report LAX`)
- `compare [A,B]` - Compare two airports (e.g., `compare LAX,SNA`)
- `region [NAME]` - Analyze region (e.g., `region "New England"`)
- `quit` - Exit

## Development

### Adding a New Data Source

1. Create provider in `providers/`:
```python
class NewProvider:
    def get_data(self, airport_code: str):
        return {...}
```

2. Wire into agent:
```python
self.new_provider = NewProvider()
data = self.new_provider.get_data(code)
```

### Adding a New Query Type

1. Add pattern to `process_query()` in `agent.py`
2. Implement `_handle_*_query()` method
3. Return (response_text, structured_data) tuple

## Performance Notes

**Query Latency**: <100ms (mock data)
- Scales linearly with number of airports
- Caching recommended for production

**Memory**: <50MB
- Conversation history in memory
- Consider database for long-running sessions

## Future Enhancements

1. **Real API Integration**: Replace mock providers with actual BTS, FAA, T100 APIs
2. **LLM Integration**: Use Claude/GPT-4 to enhance narrative explanations
3. **Web Interface**: Flask/FastAPI web dashboard
4. **Voice Support**: Add speech-to-text for voice queries
5. **Forecasting**: Multi-year traffic and ROI models
6. **Historical Validation**: Backtest scoring against past investments
7. **Risk Models**: Add regulatory, environmental, competitive risk factors

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Create Pull Request

## License

MIT License - See LICENSE file for details

## Support & Questions

For questions, issues, or suggestions, please open an issue on the repository.

---

**Built for**: Investment firms analyzing US airport modernization opportunities
**Version**: 1.0 MVP
**Last Updated**: 2026-08-09
