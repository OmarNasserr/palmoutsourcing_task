# Battery Health Report Module

A production-grade Python module for generating battery health reports from Electric Vehicle (EV) diagnostic logs.

## Quick Start

```bash
cd battery_report
python3 main.py
```

**Output**: JSON report with State of Health (SoH), cycle count, and detected anomalies.

## Documentation

📖 **[Complete Documentation →](battery_report/README.md)**

The detailed README in `battery_report/` contains:
- Input/output schemas with examples
- SoH calculation logic and thresholds (voltage imbalance, overheating, low health)
- Production architecture design (Django, PostgreSQL, Celery, monitoring)
- Design decisions and future improvements
- How to run tests

## Project Structure

```
battery_report/
├── data_simulator.py        # Mock EV diagnostic data generator
├── battery_report.py        # Health report & anomaly detection logic  
├── main.py                  # Entry point
└── tests/
    └── test_battery_report.py  # 21 unit tests (100% pass)
```

## Key Features

✅ State of Health (SoH) calculation  
✅ Anomaly detection (voltage imbalance, overheating, low health)  
✅ Realistic mock data generation (80-120 cells, voltages, temperatures)  
✅ Production-ready: comprehensive docstrings  
✅ Zero dependencies (standard library only)

---

**Requirements**: Python 3.10+
