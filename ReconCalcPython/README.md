# ReconCalc Python

A modern Python translation of the ReconCalc software reconnaissance tool.

## Features
- **Core Analyzer**: Performs set operations (union, intersection, subtraction) on execution profiles to map features to code elements.
- **Support for Formats**: Supports standard `rci` control files and handles bloated `ppf` profiles.
- **Flexible Reporting**: Generates beautiful HTML and Markdown reports.
- **Web UI**: Modern interactive dashboard built with Gradio for easy feature mapping and analysis.
- **CLI**: Command-line interface for batch processing.

## Project Structure
- `app.py`: Gradio Web UI.
- `cli.py`: Command-line interface.
- `core/`:
  - `parser.py`: Logic for parsing control files and profiles.
  - `recon_calc.py`: Core set operations and categorization logic.
  - `reporter.py`: Report generation logic.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) as its package manager.

### 1. Install dependencies and create the virtual environment
```bash
uv sync
```
This will automatically create a `.venv` folder and install all required packages (Gradio, Pandas, etc.).

## Usage

### Web UI (Gradio)
To launch the interactive web interface:
```bash
uv run python app.py
```

### CLI
To run analysis from the command line:
```bash
uv run python cli.py path/to/your.ctl -o output_report
```

## Categorization Definitions
- **CELEMS**: Common Software Elements (always executed).
- **IELEMS**: Involved Software Elements (potentially used for a feature).
- **IIELEMS**: Indispensably Involved (always used for a feature).
- **RELEMS**: Relevant Software Elements (IIELEMS - CELEMS).
- **UELEMS**: Unique Software Elements (specific to one feature).
- **SHARED**: Shared Software Elements (used by multiple features but not common).
