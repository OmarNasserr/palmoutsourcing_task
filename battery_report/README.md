# Battery Health Report Generator

## Overview

This project is a production-grade Python module that simulates Electric Vehicle (EV) battery diagnostic logs and generates comprehensive battery health reports. It demonstrates realistic battery management system (BMS) logic, including State of Health (SoH) calculation, anomaly detection, and diagnostic reporting.

The system is designed with a clear separation of concerns:
- **Data Simulation**: Generates realistic mock EV battery telemetry
- **Report Generation**: Processes diagnostic data to compute health metrics
- **Anomaly Detection**: Identifies voltage imbalance, overheating, and degradation issues

This implementation focuses on **mock data for demonstration** purposes, but the architecture and logic are designed to scale to production systems with minimal refactoring.

---

## Input Data Schema

The system processes battery diagnostic logs in JSON format. Each log represents a snapshot from a vehicle's Battery Management System (BMS).

### Schema Structure

```json
{
  "vehicle_id": "EV-12345",
  "timestamp": "2025-10-04T10:30:00.000000Z",
  "cells": [
    {
      "id": 0,
      "voltage": 4.05,
      "temperature": 35.2
    },
    {
      "id": 1,
      "voltage": 4.03,
      "temperature": 36.1
    }
  ],
  "cycle_count": 412,
  "nominal_capacity_kwh": 60.0,
  "current_capacity_kwh": 54.9
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_id` | string | Unique vehicle identifier (e.g., "EV-12345") |
| `timestamp` | string | ISO 8601 UTC timestamp of the diagnostic log |
| `cells` | array | Array of cell objects, each containing: |
| `cells[].id` | integer | Sequential cell identifier (0 to n-1) |
| `cells[].voltage` | float | Cell voltage in volts (typical: 3.8-4.2V for lithium-ion) |
| `cells[].temperature` | float | Cell temperature in Celsius (typical: 25-40°C) |
| `cycle_count` | integer | Cumulative charge/discharge cycles completed |
| `nominal_capacity_kwh` | float | Manufacturer-rated battery capacity in kWh |
| `current_capacity_kwh` | float | Current measured capacity in kWh (degrades over time) |

### Data Ranges (Simulated)

- **Cell count**: 80-120 cells (typical for mid-size EVs)
- **Voltage**: 3.8-4.2V per cell (lithium-ion nominal range)
- **Temperature**: 25-45°C with occasional outliers
- **Cycle count**: 100-800 cycles
- **Capacity retention**: 80-100% of nominal capacity

---

## Logic and Calculations

### State of Health (SoH)

**Formula**: `SoH = (current_capacity_kwh / nominal_capacity_kwh) × 100`

State of Health is the primary indicator of battery degradation. It compares the current usable capacity to the original factory capacity:
- **100%**: Brand new battery, no degradation
- **90-100%**: Normal wear, minimal impact
- **80-90%**: Noticeable degradation, within spec
- **<80%**: Significant degradation, may need service

**Reasoning**: Capacity-based SoH is the industry standard because it directly correlates with user experience (driving range). In production systems, SoH may also incorporate internal resistance and power delivery metrics.

### Anomaly Detection

The system checks for three types of anomalies:

#### 1. Voltage Imbalance

**Threshold**: Max voltage - Min voltage > 0.05V (50mV)

**Logic**: Compares the highest and lowest cell voltages in the pack.

**Reasoning**: 
- Healthy battery packs maintain cells within 20-30mV of each other
- 50mV threshold provides early warning before critical imbalance
- Imbalance indicates: manufacturing defects, cell degradation, or thermal issues
- Can lead to reduced capacity and accelerated wear

#### 2. Overheating

**Threshold**: Any cell temperature > 45°C

**Logic**: Checks if any individual cell exceeds the safe temperature limit.

**Reasoning**:
- Lithium-ion optimal range: 15-40°C
- 45°C is a warning threshold (used here)
- 60°C+ risks thermal runaway
- Causes: inadequate cooling, high current draw, internal shorts, or cell degradation

#### 3. Low State of Health

**Threshold**: SoH < 80%

**Logic**: Evaluates if calculated SoH falls below the acceptable threshold.

**Reasoning**:
- 80% is the industry-standard warranty threshold
- Below 80%, users experience 20%+ range reduction
- Degradation often accelerates below this point
- Many OEMs define 80% as "end of first life" (eligible for battery replacement)

---

## How to Run

### Prerequisites

- Python 3.10 or higher
- No external dependencies required (uses standard library only)

### Execution Steps

1. **Navigate to the project directory**:
   ```bash
   cd battery_report
   ```

2. **Run the main script**:
   ```bash
   python main.py
   ```

3. **View the output**: The script will print:
   - Input data summary
   - Battery health report (JSON format)
   - Detailed diagnostics

### Running Tests (Optional)

```bash
python -m pytest tests/test_battery_report.py -v
```

Or run tests manually:
```bash
python tests/test_battery_report.py
```

---

## Example Output

### Console Output

```
Generating mock EV diagnostic data...

============================================================
INPUT DATA SUMMARY
============================================================
Vehicle ID: EV-45821
Timestamp: 2025-10-04T10:30:00.000000Z
Number of Cells: 96
Cycle Count: 412
Nominal Capacity: 60.0 kWh
Current Capacity: 54.9 kWh

============================================================
BATTERY HEALTH REPORT
============================================================
{
  "battery_soh": 91.5,
  "cycle_count": 412,
  "anomalies": [
    "Voltage imbalance detected"
  ]
}

============================================================
DETAILED DIAGNOSTICS
============================================================
Voltage Range: 3.852V - 4.132V
Voltage Spread: 0.280V
Temperature Range: 26.45°C - 44.12°C
Average Temperature: 34.28°C

⚠️  1 anomalie(s) detected!
```

### Report JSON Schema

```json
{
  "battery_soh": 91.5,
  "cycle_count": 412,
  "anomalies": ["Voltage imbalance detected"]
}
```

**Fields**:
- `battery_soh` (float): State of Health as a percentage (0-100)
- `cycle_count` (integer): Number of charge/discharge cycles
- `anomalies` (array): List of detected issues (empty if healthy)

---

## Design Decisions

### Why Pure Python (No Framework/ORM)?

This project intentionally uses **pure Python with no external dependencies** for several reasons:

1. **Mock/Demo Purpose**: The goal is to demonstrate battery health logic, not build a full application framework
2. **Portability**: Zero dependencies make it easy to run anywhere, integrate into any system
3. **Educational Clarity**: Focus on the core algorithms without framework abstraction
4. **Testing & CI**: Lightweight, fast execution for unit tests and continuous integration

### Why JSON Structure for Cells?

The cell data is stored as a **JSON array within the diagnostic log**, not as a separate normalized table:

**Rationale**:
- **Temporal Snapshot**: Each diagnostic log is a point-in-time snapshot; cells belong exclusively to that snapshot
- **Immutability**: Logs are typically write-once, read-many (WORM) data
- **Query Patterns**: Most queries retrieve entire logs, not individual cells
- **Simplicity**: Avoids joins and foreign key management for time-series data

**When to Normalize**:
If you need to:
- Query cell-level trends over time (e.g., "show me cell #42's voltage history")
- Perform aggregations per cell across logs
- Track cell replacement or individual cell metadata

In those cases, you'd create a separate `battery_cells` table with a foreign key to the log.

---

## Production Architecture (Bonus)

### How This Would Scale in a Real EV Fleet

In a production environment, this logic would be embedded in a full-stack system:

#### High-Level Architecture

```
┌─────────────────┐
│   EV Vehicles   │  (BMS sends telemetry via cellular/WiFi)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   API Gateway / Load Balancer            │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│   Django REST API (Python)                               │
│   - Endpoints: POST /api/diagnostics, GET /api/reports  │
│   - Authentication: JWT tokens                           │
│   - Validation: Serializer models                          │
└────────┬────────────────────────────────────────────────┘
         │
         ├──────────► ┌─────────────────────────────────┐
         │            │   Celery Task Queue (RabbitMQ)     │
         │            │   - Async report generation      │
         │            │   - Batch processing             │
         │            └─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│   PostgreSQL Database                                    │
│   ┌─────────────────────────────────────────────────┐  │
│   │  vehicles (id, vin, model, manufacture_date)    │  │
│   └─────────────────────────────────────────────────┘  │
│   ┌─────────────────────────────────────────────────┐  │
│   │  diagnostic_logs                                 │  │
│   │  - id (PK)                                       │  │
│   │  - vehicle_id (FK)                               │  │
│   │  - timestamp                                     │  │
│   │  - cells (JSONB field for cell array)           │  │
│   │  - cycle_count                                   │  │
│   │  - nominal_capacity_kwh                          │  │
│   │  - current_capacity_kwh                          │  │
│   │  - indexed on: vehicle_id, timestamp             │  │
│   └─────────────────────────────────────────────────┘  │
│   ┌─────────────────────────────────────────────────┐  │
│   │  battery_reports                                 │  │
│   │  - id (PK)                                       │  │
│   │  - diagnostic_log_id (FK)                        │  │
│   │  - battery_soh                                   │  │
│   │  - anomalies (JSONB array)                       │  │
│   │  - generated_at                                  │  │
│   └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│   Monitoring & Alerting                                 │
│   - Prometheus + Grafana (metrics dashboards)           │
│   - ElasticSearch (log analysis)                        │
└─────────────────────────────────────────────────────────┘
```

#### Technology Stack

| Component | Technology            | Purpose |
|-----------|-----------------------|---------|
| **Backend API** | Django REST Framework | RESTful API for data ingestion and retrieval |
| **Database** | PostgreSQL            | Persistent storage with JSONB support for cell arrays |
| **Task Queue** | Celery + RabbitMq     | Asynchronous report generation for high-throughput processing |
| **Validation** | Serializer            | Schema validation and type safety for incoming data |
| **Caching** | Redis                 | Cache frequently accessed reports and vehicle metadata |
| **Monitoring** | Prometheus + Grafana  | Real-time metrics (SoH trends, anomaly rates) |
| **Log Storage** | ElasticSearch         | Time-series log indexing for historical analysis |
| **Frontend** | React + TypeScript    | Customer dashboard showing battery health trends |

#### Key Design Choices

1. **PostgreSQL JSONB for Cells**:
   - Stores cell arrays as JSONB (not separate table)
   - Allows querying: `WHERE cells @> '[{"voltage": {"$gt": 4.2}}]'`
   - Maintains atomicity of snapshots
   - Indexed using GIN indexes for JSONB queries

2. **When to Normalize Cells**:
   ```sql
   -- Normalize if you need per-cell trend analysis
   CREATE TABLE battery_cells (
       id SERIAL PRIMARY KEY,
       diagnostic_log_id INTEGER REFERENCES diagnostic_logs(id),
       cell_id INTEGER,
       voltage FLOAT,
       temperature FLOAT,
       INDEX idx_cell_trends (vehicle_id, cell_id, timestamp)
   );
   ```
   **Trigger**: If queries like "show me cell #42's voltage over 6 months" become common.

3. **Celery for Async Processing**:
   - Vehicles POST diagnostic data → queued immediately
   - Report generation happens asynchronously
   - Prevents API blocking during heavy computation
   - Enables batch processing of 1000s of vehicles

4. **Microservices (Future)**:
   - `diagnostic-ingestion-service`: Receives BMS telemetry
   - `report-generation-service`: Runs health calculations
   - `alerting-service`: Monitors anomalies and sends notifications
   - `trend-analysis-service`: Machine learning for predictive maintenance

#### API Example (Production)

**POST /api/v1/diagnostics**
```json
// Request
{
  "vehicle_id": "EV-12345",
  "timestamp": "2025-10-04T10:30:00Z",
  "cells": [...],
  "cycle_count": 412,
  "nominal_capacity_kwh": 60.0,
  "current_capacity_kwh": 54.9
}

// Response (202 Accepted)
{
  "message": "Diagnostic log received",
  "log_id": "a3b5c7d9-1234-5678-90ab-cdef12345678",
  "status": "processing"
}
```

**GET /api/v1/reports/{log_id}**
```json
// Response
{
  "log_id": "a3b5c7d9-1234-5678-90ab-cdef12345678",
  "vehicle_id": "EV-12345",
  "battery_soh": 91.5,
  "cycle_count": 412,
  "anomalies": ["Voltage imbalance detected"],
  "generated_at": "2025-10-04T10:30:02Z"
}
```
