"""
Main Entry Point

Entry point that imports mock data, generates a battery health report,
and prints it as formatted JSON.
"""

import json
from data_simulator import generate_mock_diagnostic_log
from battery_report import BatteryReport


def main() -> None:
    """
    Main execution function.
    
    Workflow:
        1. Generate mock EV diagnostic data
        2. Create BatteryReport instance
        3. Generate health report
        4. Output formatted JSON to stdout
    """
    # Generate mock diagnostic data
    print("Generating mock EV diagnostic data...\n")
    diagnostic_data = generate_mock_diagnostic_log()
    
    # Display input summary
    print("=" * 60)
    print("INPUT DATA SUMMARY")
    print("=" * 60)
    print(f"Vehicle ID: {diagnostic_data['vehicle_id']}")
    print(f"Timestamp: {diagnostic_data['timestamp']}")
    print(f"Number of Cells: {len(diagnostic_data['cells'])}")
    print(f"Cycle Count: {diagnostic_data['cycle_count']}")
    print(f"Nominal Capacity: {diagnostic_data['nominal_capacity_kwh']} kWh")
    print(f"Current Capacity: {diagnostic_data['current_capacity_kwh']} kWh")
    print()
    
    # Generate battery health report
    print("=" * 60)
    print("BATTERY HEALTH REPORT")
    print("=" * 60)
    report = BatteryReport(diagnostic_data).generate_report()
    
    # Print formatted JSON report
    print(json.dumps(report, indent=2))
    print()
    
    # Print detailed diagnostics (optional, for demonstration)
    print("=" * 60)
    print("DETAILED DIAGNOSTICS")
    print("=" * 60)
    
    voltages = [cell["voltage"] for cell in diagnostic_data["cells"]]
    temperatures = [cell["temperature"] for cell in diagnostic_data["cells"]]
    
    print(f"Voltage Range: {min(voltages):.3f}V - {max(voltages):.3f}V")
    print(f"Voltage Spread: {max(voltages) - min(voltages):.3f}V")
    print(f"Temperature Range: {min(temperatures):.2f}°C - {max(temperatures):.2f}°C")
    print(f"Average Temperature: {sum(temperatures) / len(temperatures):.2f}°C")
    
    if report["anomalies"]:
        print(f"\n⚠️  {len(report['anomalies'])} anomalie(s) detected!")
    else:
        print("\n✓ No anomalies detected - battery is healthy")


if __name__ == "__main__":
    main()
