
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

Key goals of this README
-----------------------

- Provide a concise description of what's in the repository.
- Explain how to build the C/C++ example(s) with CMake.
- Show how to find and run important scripts and where configuration lives.
- Give quick troubleshooting and next-step guidance.

Repository layout (important folders)
-----------------------------------

- `c/` — C/C++ sources and a top-level `CMakeLists.txt`. Contains `main.cpp` and a small sample executable.
- `conf/` — configuration snippets, CMake backups and utility files.
- `db/` — SQL queries and pipeline SQL used by data processing.
- `doc/` — assorted PDF docs, spreadsheets and reference material.
- `python/` — Python scripts and service helpers (look inside for runnable scripts).
- `schema/` — XML schema artefacts (e.g., `kraken_synthetic.xml`).
- `nginx/`, `grafana/`, `pve/`, `spark/`, `tensorflow/` — supporting configs and queries.

Files of interest
-----------------

- `c/CMakeLists.txt` — tiny CMake project (builds `c/main.cpp`).
- `c/main.cpp` — simple "Hello, World" C++ example.
- `run-all.sh`, `run-all1.sh`, `run-all2.sh` — orchestration shell scripts (bash).
- `setup.py` — not present in the repository root (if you expect a Python package, add one or check `python/`).

Building the C/C++ sample (cross-platform)
-----------------------------------------

This repo includes a minimal CMake project in `c/` that demonstrates how a C++ component is built.

On Windows (PowerShell), using the Visual Studio generator or MinGW, run (from repo root):

```powershell
# Create an out-of-source build and compile
cd c
cmake -S . -B build -G "Visual Studio 17 2022" # or omit -G to let CMake pick a default
cmake --build build --config Release

# Run the produced executable (path depends on generator); with the simple setup it will be under build/Release or build/bin
& .\build\Release\C.exe
```

Cross-platform (Linux/macOS / WSL / Git Bash):

```bash
cd c
mkdir -p build
cd build
cmake ..
cmake --build . --config Release
./C
```

Notes
-----

- Many of the provided scripts are Bash shell scripts. On Windows use WSL, Git Bash, or convert scripts to PowerShell if needed.
- The repository contains multiple experimental and backup files (e.g., `*-1.c` files, `cmake-build-debug/`). Treat this repository as a lab rather than a packaged release.
- A `setup.py` was not present in the root when this README was generated. If you plan to publish Python packages, move relevant scripts into `python/` and add a proper package manifest.

Running Python scripts
----------------------

Look under the `python/` directory for runnable scripts. Typical workflow:

```powershell
cd python
# Review scripts: ls
# Run a script with your active Python environment
python .\your_script.py
```

If you use virtual environments:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # if one exists, otherwise install what's needed
```

Data, configuration, and dashboards
----------------------------------

- `db/` contains SQL used in pipelines (InfluxDB/Timescale/regular SQL variants). Use these queries as starting points for building dashboards.
- `grafana/` contains at least one query file for Grafana.

Contributing and development notes
---------------------------------

- This repo appears to be a personal/research workspace. If you want to collaborate, consider:
	- Cleaning up experimental files and consolidating working scripts into `python/` and `c/`.
	- Adding a `LICENSE` file and a top-level `CONTRIBUTING.md`.
	- Adding a `requirements.txt` or `pyproject.toml` for Python dependencies.

Troubleshooting
---------------

- "CMake can't find a generator": install Visual Studio C++ workload or use WSL with a Unix toolchain.
- "Shell scripts fail on Windows": run them inside WSL or Git Bash, or port commonly used scripts to PowerShell.
- If a script references external APIs (Oanda, Kraken, Twitter), ensure credentials and `conf/` files are present and kept secure.

Next steps (recommended)
------------------------

1. Add a repository `LICENSE` to clarify reuse.
2. Consolidate runnable Python utilities into `python/` and add a `requirements.txt`.
3. Remove or archive clearly experimental copies (files with `-1` suffix) to reduce noise.
4. Add a short `CONTRIBUTING.md` describing how to run the main experiments and where persistent data should live.

Contact / Attribution
---------------------

This README was generated by inspecting the workspace. If you want a tailored README for publishing a package or for onboarding teammates, tell me which component(s) you want to document in more detail (for example: the ETL flow, a Python service, or the C++ components).

