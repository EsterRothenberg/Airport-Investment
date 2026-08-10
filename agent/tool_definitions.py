TOOLS = [
    {
        "type": "function",
        "name": "analyze_airport",
        "description": (
            "Analyze a U.S. airport for modernization or terminal "
            "expansion opportunity. Returns traffic metrics, operational "
            "metrics, deterministic KPI scores, and the final expansion "
            "opportunity score."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "airport_code": {
                    "type": "string",
                    "description": (
                        "Three-letter IATA airport code, for example "
                        "SFO, LAX, ANC, JFK, ATL."
                    ),
                }
            },
            "required": ["airport_code"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "compare_airports",
        "description": (
            "Compare two or more U.S. airports using traffic, capacity, "
            "operational pressure, network value, and expansion "
            "opportunity scores."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "airport_codes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 2,
                    "description": (
                        "List of IATA airport codes, for example ['LAX', 'SNA']."
                    ),
                }
            },
            "required": ["airport_codes"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_long_haul_analysis",
        "description": (
            "Analyze long-haul flight activity for one U.S. airport. "
            "Returns total performed passenger-service departures, "
            "long-haul departures, long-haul departure share, and "
            "route count. Long-haul is defined as a nonstop segment "
            "of at least 3,000 miles."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "airport_code": {
                    "type": "string",
                    "description": "Three-letter IATA airport code.",
                }
            },
            "required": ["airport_code"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "rank_airports",
        "description": (
            "Rank a supplied list of U.S. airports by deterministic "
            "Expansion Opportunity Score."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "airport_codes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "description": ("List of U.S. airport IATA codes to rank."),
                }
            },
            "required": ["airport_codes"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "find_airports",
        "description": (
            "Find U.S. airports by IATA code, city, airport name, "
            "or one or more U.S. state codes. "
            "For geographic regions such as New England, Midwest, "
            "Southeast, West Coast, or any other area, first translate "
            "the geographic concept into the appropriate U.S. state codes "
            "and pass them in states."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "states": {
                    "type": [
                        "array",
                        "null",
                    ],
                    "items": {
                        "type": "string",
                    },
                    "description": (
                        "U.S. two-letter state codes, for example "
                        "['CA'] or ['MA','CT','RI']."
                    ),
                },
                "city": {
                    "type": [
                        "string",
                        "null",
                    ],
                    "description": ("City or municipality name."),
                },
                "airport_code": {
                    "type": [
                        "string",
                        "null",
                    ],
                    "description": ("Three-letter IATA code."),
                },
                "name_query": {
                    "type": [
                        "string",
                        "null",
                    ],
                    "description": ("Airport name or part of its name."),
                },
            },
            "required": [
                "states",
                "city",
                "airport_code",
                "name_query",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "rank_airports_by_geography",
        "description": (
            "Rank commercial U.S. airports located in one or more "
            "U.S. states using the deterministic Expansion Opportunity Score. "
            "Use this for questions asking which airports in a geographic "
            "area are strongest candidates for modernization or expansion. "
            "Translate named U.S. regions into state codes before calling."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "states": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                    "description": ("U.S. two-letter state codes."),
                },
                "max_airports": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": ("Maximum number of ranked airports to return."),
                },
            },
            "required": [
                "states",
                "max_airports",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
