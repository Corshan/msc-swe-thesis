# MSc in Software Engineering Thesis — Reproducibility Pack
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21612993.svg)](https://doi.org/10.5281/zenodo.21612993)

This repository is a **Reproducibility Pack** which contains all relevant materials required to replicate the work carried out as part of this MSc thesis.

---

## Repository Structure

```
msc-swe-thesis/
├── evaluation/                 # Evaluation scripts and mappings for architectural recovery
├── literature-review/          # Literature search artefacts
│   ├── Relevant(ACM).csv
│   ├── Relevant(IEEE).csv
│   ├── Relevant(Science_direct).csv
│   └── lit_review_paper_clean_up.ipynb
│
├── recon_data/                 # Output artefacts from the architectural recovery tool
├── ReconCalc/                  # Original Software Reconnaissance tool (Perl)
│   ├── bin/                    # Perl scripts (reconnaissance, reporter, etc.)
│   ├── doc/                    # Tool documentation (PDF/PS)
│   └── example/                # Example control file and test case profiles
│
├── ReconCalcPython/            # Python translation of ReconCalc
│   ├── app.py                  # Streamlit web UI
│   ├── cli.py                  # Command-line interface
│   ├── pyproject.toml          # Project metadata and dependencies (uv)
│   ├── uv.lock                 # Locked dependency versions
│   └── core/
│       ├── parser.py           # Control file and profile parser
│       ├── recon_calc.py       # Core set-operation logic
│       └── reporter.py         # HTML and Markdown report generation
│
└── tool/                       # Architectural Recovery Tool (Python)
    ├── arch_recovery/          # Core recovery logic
    ├── pyproject.toml          # Project metadata and dependencies (uv)
    └── uv.lock                 # Locked dependency versions
```

---

## Components

### 1. Literature Review (`literature-review/`)

Contains the results of the systematic literature search conducted across three databases:

| File | Source |
|---|---|
| `Relevant(ACM).csv` | ACM Digital Library |
| `Relevant(IEEE).csv` | IEEE Xplore |
| `Relevant(Science_direct).csv` | ScienceDirect |
| `lit_review_paper_clean_up.ipynb` | Jupyter Notebook for processing and de-duplicating results |

---

### 2. ReconCalc — Original Perl Tool (`ReconCalc/`)

A **Software Reconnaissance** tool that maps software features to the code elements (procedures) that implement them, using set operations on execution profiles.

See [`ReconCalc/doc/`](./ReconCalc/doc/) for the original tool documentation.

**Example usage (requires Perl):**
```bash
cd ReconCalc/example
../bin/reconnaissance house.ctl
```

---

### 3. ReconCalcPython — Python Translation (`ReconCalcPython/`)

A modern Python re-implementation of ReconCalc with a Streamlit web interface and CLI.

> Requires [uv](https://docs.astral.sh/uv/) — a fast Python package manager.

**Setup:**
```bash
cd ReconCalcPython
uv sync          # Creates .venv and installs all dependencies
```

**Launch the web UI:**
```bash
uv run streamlit run app.py
# Opens at http://localhost:8501
```

**Run from the command line:**
```bash
uv run python cli.py path/to/your.ctl -o output_report
```

See [`ReconCalcPython/README.md`](./ReconCalcPython/README.md) for full details.

---

### 4. Architectural Recovery Tool (`tool/`)

A Python-based tool for architectural recovery that instruments source code, traces execution, computes feature sets, and generates architectural diagrams and decompositions.

> Requires [uv](https://docs.astral.sh/uv/) — a fast Python package manager.

**Example commands:**
```bash
uv run tool instrument -p "/path/to/project" -s "/path/to/project/src" -l python
uv run tool trace -p "/path/to/project" -tc "pytest tests" -tn "test_name"
uv run tool compute -p "/path/to/project"
uv run tool diagram -p "/path/to/project"
```

---

### 5. Evaluation (`evaluation/`)

Contains scripts, manual mappings, and output results for evaluating the architectural recovery models.

- `scripts/`: Python scripts for calculating metrics (e.g., Coupling, Cohesion) and evaluating architectural recovery against ground truth.
- `mappings/`: Manual flat and structural mappings of features to architectural components.
- `output/`: Output results and metric reports.

---

### 6. Reconnaissance Data (`recon_data/`)

Contains the generated output data and artefacts produced by the architectural recovery tool during test runs, such as traces, feature sets, layout structures, decompositions, and diagrams.
