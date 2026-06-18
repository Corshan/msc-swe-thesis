# Architecture Recovery Report

## Feature Architecture Reflexion Model

This document contains the automatically recovered software architecture based on dynamic traces and static LSI mappings.

```mermaid
graph TD
    %% Styling
    classDef convergence fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef divergence fill:#f8d7da,stroke:#dc3545,stroke-width:2px;
    classDef absence fill:#fff3cd,stroke:#ffc107,stroke-width:2px,stroke-dasharray: 5 5;
    classDef feature fill:#e2e3e5,stroke:#6c757d,stroke-width:2px;
    Feature_0[Feature_0]:::feature
    Feature_1[Feature_1]:::feature

    %% Lifted Dependencies
```

## Component Details

### Feature_0
- `app.py::query`
- `app.py::__init__`
- `app.py::login`
- `app.py::logout`

### Feature_1
- `test_app.py::test_login`
- `test_app.py::test_logout`
