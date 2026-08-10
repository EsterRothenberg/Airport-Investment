# Data Sources

Large raw aviation datasets are not committed to the repository.

The application expects the following local structure:

```text
data/
├── metadata/
│   └── airports.csv
├── t100/
│   └── t100_2025.csv
└── on_time/
    ├── 2025-01.csv
    ├── ...
    └── 2025-12.csv
```

## Sources

### Airport Metadata

Airport metadata is based on the **OurAirports** open airport dataset.

[OurAirports data downloads](https://ourairports.com/data/?utm_source=chatgpt.com)

Used for airport discovery, IATA codes, cities, states, coordinates, airport type, and geographic resolution. The `airports.csv` format is documented by OurAirports.

### T-100 Segment Data

Source: **U.S. Department of Transportation — Bureau of Transportation Statistics (BTS), TranStats**.

[BTS TranStats](https://www.transtats.bts.gov/?utm_source=chatgpt.com)

The project uses 2025 T-100 segment data for route counts, distances, performed departures, and long-haul analysis.

### On-Time Performance

Source: **BTS Reporting Carrier On-Time Performance**.

[BTS Reporting Carrier On-Time Performance](https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ&utm_source=chatgpt.com)

The project uses monthly 2025 files for delays and cancellations. BTS provides this dataset by month and year and includes origin/destination, delays, cancellations, and other flight-level operational information.

## Notes

The prototype analyzes **2025**, with **2024 used as the growth baseline**.

Long-haul is defined as a nonstop segment of at least **3,000 miles**.

Raw datasets are excluded from Git because of their size and can be recreated from the public sources above.
