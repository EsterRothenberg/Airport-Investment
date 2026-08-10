# Airport Investment Intelligence Agent - Architecture

## Overview

The system helps investment analysts screen U.S. airports for modernization and terminal-expansion opportunities.

The main design principle is separation between **AI reasoning** and **quantitative analysis**:

* The LLM understands user intent, selects tools, maintains conversational context, and explains results.
* Python services calculate all aviation metrics, scores, comparisons, and rankings deterministically.

This keeps quantitative results reproducible and reduces LLM hallucination risk.

## Architecture

```text id="a76sq1"
User
  ↓
Streamlit Chat UI
  ↓
LLM Agent
  ↓
Agent Tools
  ↓
AirportService
  ├── BTS Airport Traffic
  ├── T-100 Route Data
  ├── On-Time Performance
  └── Airport Metadata
  ↓
AnalyticsService
  ↓
AirportMetrics
  ↓
ScoringService
  ↓
Expansion Opportunity Score
  ↓
LLM explanation
```

For geographic questions, the LLM translates expressions such as "New England" or "Pacific Northwest" into U.S. state codes. Airport discovery itself is then performed deterministically against the airport metadata dataset.

## Scoring Methodology

The **Expansion Opportunity Score** is a deterministic 0–100 screening metric:

| Dimension            | Weight | Main inputs                            |
| -------------------- | -----: | -------------------------------------- |
| Demand Growth        |    30% | Passenger growth, flight growth        |
| Capacity Pressure    |    25% | Load factor, flight growth             |
| Operational Pressure |    20% | Delay rate, cancellation rate          |
| Network Value        |    15% | Route count, long-haul departure share |
| Market Scale         |    10% | Passenger volume, annual departures    |

Each input is normalized to a 0–100 scale before applying the weights.

Market Scale is included to reduce the risk of ranking small airports highly solely because of unusually large percentage growth.

The score is intended for **directional screening**, not as a financial ROI estimate.

### Missing Data

Missing values are not treated as zero.

When a scoring dimension is unavailable, the remaining weights are re-normalized. A separate `data_completeness_pct` shows how much of the original weighted model could be evaluated.

For example, if Operational Pressure (20%) is unavailable, data completeness is 80%.

## Long-Haul Methodology

For this prototype, long-haul is defined as a nonstop segment of at least **3,000 miles**.

Long-haul share is calculated using performed passenger-service departures:

```text id="u1hh2h"
Long-haul departures / Total departures × 100
```

Route count is reported separately and is not used as the denominator.

## Where / How AI Is Used

### AI inside the product

The LLM is used as the conversational orchestration layer.

It is responsible for:

* Understanding natural-language questions
* Selecting the appropriate analytical tools
* Interpreting geographic expressions such as regions or cities
* Maintaining conversational follow-up context
* Explaining deterministic metrics, rankings, assumptions, and limitations

The LLM does **not** calculate aviation KPIs or investment scores. All quantitative calculations and rankings are performed by deterministic Python services.

### AI used during development

AI tools were also used as part of the development workflow.

* **GitHub Copilot** was used to accelerate initial code generation and boilerplate implementation.
* **ChatGPT** was used for architecture design, reviewing generated code, refining the scoring methodology, debugging integration issues, designing tests, and validating the system against the assignment requirements.

AI-generated code was not accepted blindly. Generated implementations were reviewed, tested against real BTS data, and changed when they did not meet the assignment requirements.

For example, initial mock/random-data approaches were replaced with real public aviation data sources, and the scoring methodology was refined after testing showed that small airports with unusually high percentage growth could be over-ranked.

## Key Tradeoffs

**Explainability over model complexity.**
A deterministic weighted score was chosen instead of an opaque ML model so rankings remain reproducible and easy to explain.

**Screening over financial valuation.**
The model identifies airports worth investigating further. It does not include construction costs, airport financials, terminal square footage, or project-level ROI.

**Public-data availability.**
Some large BTS datasets are consumed as downloaded public files rather than through live APIs. This improves reliability and keeps the prototype achievable within the assignment timeframe.

**Unmet demand is directional.**
The available data does not directly measure denied passenger demand. Growth, load factor, capacity pressure, and delays are therefore treated as indicators rather than a quantified number of unmet passengers or flights.

## Data Sources

* U.S. DOT/BTS airport traffic data - passengers, seats, departures and load factor
* BTS T-100 Segment data - routes, distance and performed departures
* BTS Reporting Carrier On-Time Performance - delays and cancellations
* U.S. airport metadata - airport and geographic resolution

The prototype analyzes **2025**, with **2024 used as the growth baseline**.

## Future Improvements

A production version could add gate and terminal utilization, runway constraints, airline schedule requests, airport financial data, demand forecasts, project costs, and ROI/IRR modeling.
