# MSc in Software Engineering Thesis — Reproducibility Pack

This repository is a **Reproducibility Pack** which contains all relevant materials required to replicate the work carried out as part of this MSc thesis.

---

## Repository Structure

```
msc-swe-thesis/
├── literature-review/          # Literature search artefacts
│   ├── Relevant(ACM).csv
│   ├── Relevant(IEEE).csv
│   ├── Relevant(Science_direct).csv
│   └── lit_review_paper_clean_up.ipynb
│
├── ReconCalc/                  # Original Software Reconnaissance tool (Perl)
│   ├── bin/                    # Perl scripts (reconnaissance, reporter, etc.)
│   ├── doc/                    # Tool documentation (PDF/PS)
│   └── example/                # Example control file and test case profiles
│
└── ReconCalcPython/            # Python translation of ReconCalc
    ├── app.py                  # Streamlit web UI
    ├── cli.py                  # Command-line interface
    ├── pyproject.toml          # Project metadata and dependencies (uv)
    ├── uv.lock                 # Locked dependency versions
    └── core/
        ├── parser.py           # Control file and profile parser
        ├── recon_calc.py       # Core set-operation logic
        └── reporter.py         # HTML and Markdown report generation
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
