"""
Data Simulator Module

Generates realistic mock EV diagnostic JSON logs containing cell voltages,
temperatures, cycle count, nominal capacity, and current capacity.
"""

import random
from datetime import datetime
from typing import Dict, List, Any


def generate_mock_diagnostic_log() -> Dict[str, Any]:
    """
    Generate a realistic mock EV battery diagnostic log.
    
    This function simulates data from an electric vehicle's battery management system,
    including individual cell metrics, cycle counts, and capacity measurements.
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - vehicle_id: Unique vehicle identifier
            - timestamp: ISO 8601 formatted timestamp
            - cells: List of cell data (id, voltage, temperature)
            - cycle_count: Number of charge/discharge cycles
            - nominal_capacity_kwh: Manufacturer-rated capacity
            - current_capacity_kwh: Current measured capacity
    
    Data Simulation Strategy:
        - Cell count: Random between 80-120 cells (typical for EVs)
        - Voltages: 3.8-4.2V per cell (lithium-ion nominal range)
        - Temperatures: 25-45°C with occasional outliers for anomaly testing
        - Cycle count: 100-800 cycles (representing various vehicle ages)
        - Capacity degradation: Current capacity is 80-100% of nominal
    """
    # Generate vehicle ID
    vehicle_id = f"EV-{random.randint(10000, 99999)}"
    
    # Current timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Generate cell count (typical EV battery has 80-120 cells)
    cell_count = random.randint(80, 120)
    
    # Generate cell data with potential anomalies
    cells = []
    base_voltage = random.uniform(3.9, 4.1)  # Base voltage for all cells
    
    for i in range(cell_count):
        # Add small variation to simulate real-world imbalance
        # Most cells will be within 0.02V of base, but some may drift further
        voltage_variation = random.gauss(0, 0.015)  # Normal distribution
        voltage = base_voltage + voltage_variation
        
        # Clamp voltage to realistic bounds
        voltage = max(3.8, min(4.2, voltage))
        
        # Temperature simulation
        # Most cells at normal operating temperature, occasional hot spots
        if random.random() < 0.05:  # 5% chance of hot cell
            temperature = random.uniform(43, 48)
        else:
            temperature = random.uniform(25, 42)
        
        cells.append({
            "id": i,
            "voltage": round(voltage, 3),
            "temperature": round(temperature, 2)
        })
    
    # Optionally introduce voltage imbalance for testing
    if random.random() < 0.3:  # 30% chance of imbalance
        # Make a few cells significantly different
        imbalance_count = random.randint(1, 3)
        for _ in range(imbalance_count):
            cell_idx = random.randint(0, cell_count - 1)
            if random.random() < 0.5:
                cells[cell_idx]["voltage"] = round(random.uniform(3.80, 3.88), 3)
            else:
                cells[cell_idx]["voltage"] = round(random.uniform(4.12, 4.20), 3)
    
    # Generate cycle count (100-800 cycles representing various ages)
    cycle_count = random.randint(100, 800)
    
    # Nominal capacity (fixed manufacturer rating)
    nominal_capacity_kwh = 60.0
    
    # Current capacity degrades with cycles
    # Newer batteries: 95-100%, older batteries: 80-95%
    if cycle_count < 300:
        capacity_percentage = random.uniform(0.95, 1.0)
    elif cycle_count < 600:
        capacity_percentage = random.uniform(0.85, 0.95)
    else:
        capacity_percentage = random.uniform(0.80, 0.90)

    current_capacity_kwh = round(nominal_capacity_kwh * capacity_percentage, 2)
    
    return {
        "vehicle_id": vehicle_id,
        "timestamp": timestamp,
        "cells": cells,
        "cycle_count": cycle_count,
        "nominal_capacity_kwh": nominal_capacity_kwh,
        "current_capacity_kwh": current_capacity_kwh
    }