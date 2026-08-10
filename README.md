# Airport Investment Intelligence Agent

AI-powered screening tool for identifying promising U.S. airport modernization and terminal-expansion opportunities.

The system combines public aviation data, deterministic analytics, and an LLM-based conversational agent. The LLM is responsible for understanding user intent, selecting analytical tools, and explaining results. All quantitative metrics, rankings, and investment scores are calculated by deterministic Python services.

## Main Capabilities

The agent can:

* Analyze an individual U.S. airport.
* Compare multiple airports.
* Rank airports within a U.S. geographic area.
* Resolve airports from IATA codes, cities, states, or geographic regions.
* Calculate passenger and flight growth.
* Calculate load factor and capacity pressure.
* Analyze delays and cancellations.
* Calculate long-haul departure share.
* Evaluate network importance.
* Produce a deterministic Expansion Opportunity Score.
* Support conversational follow-up questions.
* Explicitly communicate assumptions, missing data, and analytical limitations.

Example questions:

```text
Which airports in New England are strong candidates for terminal expansion?

Compare LAX and Santa Ana airport congestion levels.

What percentage of flights from Anchorage are long-haul?

What is the unmet flight demand at SFO and why?

Which airports in Florida look strongest for modernization investment?

Which airports in the Pacific Northwest look strongest for expansion?
```

## Architecture

```text
User
 │
 ▼
Streamlit Chat UI
 │
 ▼
LLM Agent
 │
 ├── understand intent
 ├── maintain conversation context
 └── select tools
 │
 ▼
Agent Tools
 │
 ├── analyze_airport
 ├── compare_airports
 ├── get_long_haul_analysis
 ├── rank_airports
 ├── find_airports
 └── rank_airports_by_geography
 │
 ▼
Airport Service
 │
 ├── BTS Airport Traffic API
 ├── T-100 Segment Provider
 ├── On-Time Performance Provider
 └── Airport Metadata Resolver
 │
 ▼
Analytics Service
 │
 ▼
Airport Metrics
 │
 ▼
Scoring Service
 │
 ▼
Deterministic Expansion Opportunity Score
 │
 ▼
LLM explanation
```

## Data Sources

### U.S. DOT / BTS Airport Traffic

Used for:

* Passenger volume
* Seat capacity
* Departures
* Passenger growth
* Flight growth
* Load factor

The prototype analyzes 2025 traffic and uses 2024 as the growth baseline.

### BTS T-100 Segment

Used for:

* Origin-destination routes
* Route count
* Distance
* Performed departures
* Long-haul analysis

Long-haul is defined by the prototype as a nonstop segment of at least 3,000 miles.

The long-haul percentage is calculated from performed passenger-service departures, not from route count.

### BTS Reporting Carrier On-Time Performance

Used for:

* Arrival delays
* Cancellation rate
* Operational pressure

A delayed flight is defined as a completed flight arriving at least 15 minutes late.

### Airport Metadata

Airport metadata is used only for airport discovery and geographic resolution.

The analytical metrics and scoring remain based on BTS aviation data.

## Scoring Methodology

The Expansion Opportunity Score is a deterministic 0-100 screening metric composed of five dimensions.

### Demand Growth - 30%

Based on:

* Passenger growth: 60%
* Flight growth: 40%

Normalization ranges:

```text
Passenger Growth: -5% → 0, 15% → 100
Flight Growth:    -5% → 0, 15% → 100
```

### Capacity Pressure - 25%

Based on:

* Load factor: 70%
* Flight growth: 30%

Normalization:

```text
Load Factor: 60% → 0, 90% → 100
Flight Growth: -5% → 0, 15% → 100
```

### Operational Pressure - 20%

Based on:

* Delay rate: 75%
* Cancellation rate: 25%

Normalization:

```text
Delay Rate:        5% → 0, 30% → 100
Cancellation Rate: 0% → 0, 5% → 100
```

### Network Value - 15%

Based on:

* Route count: 60%
* Long-haul departure share: 40%

Normalization:

```text
Route Count:       10 → 0, 150 → 100
Long-Haul Share:   0% → 0, 20% → 100
```

### Market Scale - 10%

Based on:

* Passenger volume: 70%
* Annual departures: 30%

Normalization:

```text
Passenger Volume: 500,000 → 0, 30,000,000 → 100
Departures:          5,000 → 0,    200,000 → 100
```

Market Scale was added to reduce the risk of over-ranking very small airports solely because of unusually high percentage growth.

The final score is:

```text
Expansion Opportunity Score =
    Demand Growth        × 30%
  + Capacity Pressure    × 25%
  + Operational Pressure × 20%
  + Network Value        × 15%
  + Market Scale         × 10%
```

## Missing Data

Missing data is never treated as zero.

If a scoring dimension cannot be calculated, its weight is excluded and the remaining available weights are re-normalized.

A separate `data_completeness_pct` indicates how much of the weighted scoring model could be evaluated.

Example:

```text
Operational Pressure missing
Operational weight = 20%

Data Completeness = 80%
```

Data completeness is not a statistical confidence interval.

## Where AI Is Used

The LLM is intentionally not responsible for quantitative calculations.

AI is used for:

* Understanding natural-language questions.
* Resolving geographic intent.
* Choosing the appropriate analytical tools.
* Maintaining conversational context.
* Explaining deterministic results.
* Summarizing assumptions and limitations.

AI is not used for:

* Calculating airport metrics.
* Calculating KPI scores.
* Ranking airports.
* Inventing missing aviation data.

This separation reduces hallucination risk and makes the analytical output reproducible.

## Handling Unmet Demand

The prototype does not directly quantify denied or unmet passenger demand.

For questions such as:

```text
What is the unmet flight demand at SFO?
```

the system uses demand-pressure indicators such as:

* Passenger growth
* Flight growth
* Load factor
* Capacity pressure
* Operational delays

These are treated as directional proxies.

The agent explicitly states that a true unmet-demand estimate would require additional data such as denied bookings, waitlists, airline slot requests, unconstrained demand forecasts, or fare-based demand signals.

## Key Tradeoffs

### Deterministic scoring vs. LLM scoring

Deterministic scoring was chosen to make rankings reproducible, testable, and explainable.

The LLM interprets results but cannot modify scores.

### Local datasets vs. additional APIs

Some BTS datasets are consumed from downloaded public files rather than additional online APIs.

This reduces dependency on fragile external endpoints and keeps the prototype achievable within the 24-hour assignment constraint.

### Historical completeness vs. recency

The prototype uses 2025 as the analysis year because it provides a consistent complete period across data sources.

2024 is used as the year-over-year growth baseline.

### Breadth vs. analytical depth

The system is designed as an investment-screening tool rather than a full airport financial model.

It does not include:

* Project construction costs
* Airport concession economics
* Terminal square footage
* Gate-level utilization
* Airline lease structures
* Detailed runway capacity
* Financial ROI projections

These would be natural extensions for a production system.

## Running the Project

### Prerequisites

* Docker
* Docker Compose
* OpenAI API key

Create:

```text
.env
```

with:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=your_model_here
```
### Required Data

Large BTS datasets are not committed to the repository due to their size.
Before running the application, download and place the required datasets according to the instructions in [`data/README.md`](data/README.md).
The application expects the required T-100, On-Time Performance, and airport metadata files to be available locally.
### Run

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

### Stop

```bash
docker compose down
```

## Tests

```bash
pytest -v
```

## Project Scope

The current prototype supports U.S. airports only.

If asked about airports outside the United States, the agent explicitly communicates that the required deterministic aviation coverage is not available and does not invent rankings.

## Optional Future Improvements

Possible production extensions include:

* Live automated ingestion of BTS datasets
* More advanced geographic search
* Gate and terminal-capacity datasets
* Runway and airspace congestion
* Airline schedule requests and denied-demand signals
* Airport financial and concession data
* Project-level ROI modeling
* Persistent caching or database storage
* FastAPI service layer
* Voice interaction
