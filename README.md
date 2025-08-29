
# nbpy — Market data tooling, ETL and analysis workspace

Overview
--------

`nbpy` is a multi-language collection of tools, scripts and small services used for market data ingestion, ETL, analytics and lightweight research experiments. The repository contains C/C++ sample programs and build scaffolding, a variety of shell and Python scripts for data processing and orchestration, SQL and configuration snippets, and documentation/artifacts used for research and operations.

This workspace looks like an evolving research/operations playground rather than a single packaged product. It gathers utilities for:

- ETL + ZMQ-based message bus patterns
- Small C/C++ utilities and example programs (CMake-based)
- Cross-rates and synthetic basket generation
- Position/portfolio entry helpers and aggregation SQL
- Text/geocoding/sentiment experiments (Twitter/RSS integrations)
- Misc monitoring and Grafana queries

# nbpy — Market data tooling, ETL and analysis workspace

## Overview

`nbpy` is a multi-language collection of tools, scripts and small services used for market data ingestion, ETL, analytics and lightweight research experiments. The repository contains C/C++ sample programs and build scaffolding, shell and Python scripts for data processing and orchestration, SQL and InfluxDB query snippets, and reference documentation.

This workspace is a research/operations playground rather than a packaged product. It gathers utilities for:

- ETL + ZMQ-based message bus patterns
- Small C/C++ utilities and example programs (CMake-based)
- Cross-rates and synthetic basket generation
- Position/portfolio entry helpers and aggregation SQL
- Text/geocoding/sentiment experiments (Twitter/RSS integrations)
- Misc monitoring and Grafana queries

## Key goals of this README

- Describe repository contents and where to find components
- Provide build instructions for the C/C++ sample
- Show representative query examples and expected outputs
- Provide sample message formats used on the message bus

## Repository layout (important folders)

- `c/` — C/C++ sources and a top-level `CMakeLists.txt`. Contains `main.cpp` and a small sample executable.
- `conf/` — configuration snippets, CMake backups and utility files.
- `db/` — SQL queries and pipeline SQL used by data processing and InfluxDB snippets.
- `doc/` — assorted PDF docs, spreadsheets and reference material.
- `python/` — Python scripts and service helpers (look inside for runnable scripts).
- `schema/` — XML schema artefacts (e.g., `kraken_synthetic.xml`).

## Files of interest

- `c/CMakeLists.txt` — tiny CMake project (builds `c/main.cpp`).
- `c/main.cpp` — simple "Hello, World" C++ example.
- `db/influxdb_query.txt` — InfluxDB query examples and continuous query patterns.
- `db/pipeline_oanda.sql` — SQL/stream examples for oanda_tick pipeline.

## Examples — queries, outputs and message formats

The repository contains many small examples. Below are concrete query examples taken from `db/` plus representative outputs and message formats you can expect while using the project.

### InfluxDB query examples

Representative InfluxQL snippets (from `db/influxdb_query.txt`):

```sql
-- create a continuous query that counts tweets mentioning 'euro'
CREATE CONTINUOUS QUERY "count_euro" ON "twitter" \
BEGIN SELECT count("id") INTO "count_euro" FROM "tweet" WHERE "text" like '%euro%' GROUP BY time(1m) END

-- select recent tick bids for USD_JPY
SELECT "bid" FROM "tick" WHERE "instrument"='USD_JPY' AND time >= '2017-02-08T17:04:26Z' AND time <= '2017-02-08T18:49:26Z'

-- holt-winters forecasting example
SELECT holt_winters(first("bid"), 5, 2) FROM "oanda_tick" WHERE "instrument"='USD_JPY' AND time > now() - 5m GROUP BY time(1m)
```

Expected (simplified) InfluxDB JSON-style result for the holt_winters query:

```json
{
	"results": [
		{
			"series": [
				{
					"name": "holt_winters",
					"columns": ["time","holt_winters"],
					"values": [
						["2025-08-29T12:00:00Z", 151.2345],
						["2025-08-29T12:01:00Z", 151.2360]
					]
				}
			]
		}
	]
}
```

> Note: Actual Influx responses depend on your InfluxDB version and client library. The shape above is a representative example.

### SQL / streaming examples (Postgres / materialized/continuous views)

Snippets from `db/pipeline_oanda.sql` used to create continuous views / streams:

```sql
-- create a continuous view from a streaming source
CREATE CONTINUOUS VIEW oanda_tick_view AS SELECT timestmp, instrument, bid, ask FROM oanda_tick;

-- create a view that keeps the latest tick per instrument
CREATE CONTINUOUS VIEW oanda_last_tick_transform AS
	SELECT DISTINCT instrument, MAX(timestmp) AS last_ts, bid, ask
	FROM oanda_tick
	GROUP BY instrument, bid, ask;

-- sample aggregation
SELECT DISTINCT(instrument), avg(bid), avg(ask) FROM oanda_tick_view GROUP BY instrument LIMIT 150;
```

Representative SQL result (tabular):

| instrument | avg(bid) | avg(ask) |
|------------|----------:|---------:|
| USD_JPY    | 151.2345 | 151.2348 |
| EUR_USD    | 1.0823   | 1.0825   |

### ZMQ / message bus and tick message examples

The repository uses message-bus patterns and stream-like payloads. Typical tick messages emitted on the bus are JSON objects like this:

```json
{
	"timestmp": "2025-08-29T12:34:56.123Z",
	"instrument": "USD_JPY",
	"bid": 151.2345,
	"ask": 151.2348,
	"source": "oanda",
	"tick_id": "abc123"
}
```

A small ETL consumer printing a received tick might produce console output similar to:

```
[INFO] 2025-08-29T12:34:56Z Received tick: USD_JPY bid=151.2345 ask=151.2348
[DEBUG] Persisted tick to table: oanda_tick (instrument=USD_JPY timestmp=2025-08-29T12:34:56Z)
```

Another common message type in experiments is a synthetic-basket snapshot:

```json
{
	"snapshot_ts": "2025-08-29T12:35:00Z",
	"basket": "EURUSD_synthetic",
	"components": [
		{"instrument":"EUR_USD", "weight":0.6, "price":1.0823},
		{"instrument":"USD_JPY", "weight":0.4, "price":151.2345}
	],
	"value": 65.4321
}
```

### Example prints and outputs from local components

- `c/main.cpp` — running the sample C++ binary prints a single line:

```
Hello, World!
```

- Example output when querying the latest ticks from the continuous SQL view (psql style):

```
 instrument |      last_ts       |   bid    |   ask
------------+--------------------+----------+---------
 USD_JPY    | 2025-08-29 12:34:56| 151.2345 |151.2348
 EUR_USD    | 2025-08-29 12:34:55| 1.08230  |1.08250
```

## Notes

- InfluxDB uses InfluxQL or Flux depending on the version; examples above are InfluxQL-style snippets.
- The SQL shown in `db/pipeline_oanda.sql` is tailored for streaming/continuous-view engines (materialized/continuous views). Adapt to your SQL engine (TimescaleDB, Materialize, or ksqlDB) as needed.
- Protect and provision API keys (Oanda, Kraken, Twitter) in `conf/` and do not commit secrets to the repository.

## Contributing and development notes

- This repo appears to be a personal/research workspace. If you want to collaborate, consider:
	- Cleaning up experimental files and consolidating working scripts into `python/` and `c/`.
	- Adding a `LICENSE` file and a top-level `CONTRIBUTING.md`.
	- Adding a `requirements.txt` or `pyproject.toml` for Python dependencies.

## Troubleshooting

- "CMake can't find a generator": install Visual Studio C++ workload or use WSL with a Unix toolchain.
- "Shell scripts fail on Windows": run them inside WSL or Git Bash, or port commonly used scripts to PowerShell.
- If a script references external APIs (Oanda, Kraken, Twitter), ensure credentials and `conf/` files are present and kept secure.

## Next steps (recommended)

1. Add a repository `LICENSE` to clarify reuse.
2. Consolidate runnable Python utilities into `python/` and add a `requirements.txt`.
3. Remove or archive clearly experimental copies (files with `-1` suffix) to reduce noise.
4. Add a short `CONTRIBUTING.md` describing how to run the main experiments and where persistent data should live.

## Contact / Attribution

This README was generated by inspecting the workspace. If you want a tailored README for publishing a package or for onboarding teammates, tell me which component(s) you want to document in more detail (for example: the ETL flow, a Python service, or the C++ components).

