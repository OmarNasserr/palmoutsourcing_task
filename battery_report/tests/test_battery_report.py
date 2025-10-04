"""
Unit Tests for Battery Report Module

Tests the core functionality of BatteryReport class including:
- State of Health (SoH) calculation
- Voltage imbalance detection
- Overheating detection
- Low health detection
- Report generation
"""

import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from battery_report import BatteryReport


class TestBatteryReport(unittest.TestCase):
    """Test suite for BatteryReport class."""
    
    def setUp(self):
        """Set up test fixtures with sample diagnostic data."""
        self.base_data = {
            "vehicle_id": "EV-TEST-001",
            "timestamp": "2025-10-04T10:00:00Z",
            "cells": [
                {"id": 0, "voltage": 4.0, "temperature": 30.0},
                {"id": 1, "voltage": 4.0, "temperature": 31.0},
                {"id": 2, "voltage": 4.0, "temperature": 32.0},
            ],
            "cycle_count": 300,
            "nominal_capacity_kwh": 60.0,
            "current_capacity_kwh": 54.0
        }
    
    def test_calculate_state_of_health_normal(self):
        """Test SoH calculation with normal capacity."""
        report = BatteryReport(self.base_data)
        soh = report.calculate_state_of_health()
        
        # Expected: (54.0 / 60.0) * 100 = 90.0
        self.assertEqual(soh, 90.0)
    
    def test_calculate_state_of_health_perfect(self):
        """Test SoH calculation with no degradation."""
        data = self.base_data.copy()
        data["current_capacity_kwh"] = 60.0
        
        report = BatteryReport(data)
        soh = report.calculate_state_of_health()
        
        self.assertEqual(soh, 100.0)
    
    def test_calculate_state_of_health_degraded(self):
        """Test SoH calculation with significant degradation."""
        data = self.base_data.copy()
        data["current_capacity_kwh"] = 45.0
        
        report = BatteryReport(data)
        soh = report.calculate_state_of_health()
        
        # Expected: (45.0 / 60.0) * 100 = 75.0
        self.assertEqual(soh, 75.0)
    
    def test_calculate_state_of_health_zero_nominal(self):
        """Test SoH calculation with zero nominal capacity (edge case)."""
        data = self.base_data.copy()
        data["nominal_capacity_kwh"] = 0.0
        
        report = BatteryReport(data)
        soh = report.calculate_state_of_health()
        
        self.assertEqual(soh, 0.0)
    
    def test_detect_voltage_imbalance_none(self):
        """Test voltage imbalance detection with balanced cells."""
        report = BatteryReport(self.base_data)
        has_imbalance = report.detect_voltage_imbalance()
        
        # All cells at 4.0V, spread = 0V (< 0.05V threshold)
        self.assertFalse(has_imbalance)
    
    def test_detect_voltage_imbalance_minor(self):
        """Test voltage imbalance detection with minor imbalance (below threshold)."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 4.00, "temperature": 30.0},
            {"id": 1, "voltage": 4.02, "temperature": 31.0},
            {"id": 2, "voltage": 4.03, "temperature": 32.0},
        ]
        
        report = BatteryReport(data)
        has_imbalance = report.detect_voltage_imbalance()
        
        # Spread = 0.03V (< 0.05V threshold)
        self.assertFalse(has_imbalance)
    
    def test_detect_voltage_imbalance_detected(self):
        """Test voltage imbalance detection with significant imbalance."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 3.90, "temperature": 30.0},
            {"id": 1, "voltage": 4.00, "temperature": 31.0},
            {"id": 2, "voltage": 4.10, "temperature": 32.0},
        ]
        
        report = BatteryReport(data)
        has_imbalance = report.detect_voltage_imbalance()
        
        # Spread = 0.20V (> 0.05V threshold)
        self.assertTrue(has_imbalance)
    
    def test_detect_voltage_imbalance_exact_threshold(self):
        """Test voltage imbalance detection at exact threshold."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 4.00, "temperature": 30.0},
            {"id": 1, "voltage": 4.05, "temperature": 31.0},
        ]
        
        report = BatteryReport(data)
        has_imbalance = report.detect_voltage_imbalance()
        
        # Spread = 0.05V (= threshold, should not trigger)
        self.assertFalse(has_imbalance)
    
    def test_detect_voltage_imbalance_just_above_threshold(self):
        """Test voltage imbalance detection just above threshold."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 4.00, "temperature": 30.0},
            {"id": 1, "voltage": 4.06, "temperature": 31.0},
        ]
        
        report = BatteryReport(data)
        has_imbalance = report.detect_voltage_imbalance()
        
        # Spread = 0.06V (> 0.05V threshold)
        self.assertTrue(has_imbalance)
    
    def test_detect_overheating_none(self):
        """Test overheating detection with normal temperatures."""
        report = BatteryReport(self.base_data)
        is_overheating = report.detect_overheating()
        
        # All cells at 30-32°C (< 45°C threshold)
        self.assertFalse(is_overheating)
    
    def test_detect_overheating_detected(self):
        """Test overheating detection with high temperature."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 4.0, "temperature": 30.0},
            {"id": 1, "voltage": 4.0, "temperature": 48.0},
            {"id": 2, "voltage": 4.0, "temperature": 32.0},
        ]
        
        report = BatteryReport(data)
        is_overheating = report.detect_overheating()
        
        # Cell 1 at 48°C (> 45°C threshold)
        self.assertTrue(is_overheating)
    
    def test_detect_overheating_exact_threshold(self):
        """Test overheating detection at exact threshold."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 4.0, "temperature": 45.0},
        ]
        
        report = BatteryReport(data)
        is_overheating = report.detect_overheating()
        
        # Exactly 45°C (= threshold, should not trigger)
        self.assertFalse(is_overheating)
    
    def test_detect_overheating_just_above_threshold(self):
        """Test overheating detection just above threshold."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 4.0, "temperature": 45.1},
        ]
        
        report = BatteryReport(data)
        is_overheating = report.detect_overheating()
        
        # 45.1°C (> 45°C threshold)
        self.assertTrue(is_overheating)
    
    def test_detect_low_health_normal(self):
        """Test low health detection with normal SoH."""
        report = BatteryReport(self.base_data)
        soh = report.calculate_state_of_health()
        is_low = report.detect_low_health(soh)
        
        # SoH = 90% (> 80% threshold)
        self.assertFalse(is_low)
    
    def test_detect_low_health_detected(self):
        """Test low health detection with degraded battery."""
        data = self.base_data.copy()
        data["current_capacity_kwh"] = 45.0
        
        report = BatteryReport(data)
        soh = report.calculate_state_of_health()
        is_low = report.detect_low_health(soh)
        
        # SoH = 75% (< 80% threshold)
        self.assertTrue(is_low)
    
    def test_detect_low_health_exact_threshold(self):
        """Test low health detection at exact threshold."""
        data = self.base_data.copy()
        data["current_capacity_kwh"] = 48.0
        
        report = BatteryReport(data)
        soh = report.calculate_state_of_health()
        is_low = report.detect_low_health(soh)
        
        # SoH = 80% (= threshold, should not trigger)
        self.assertFalse(is_low)
    
    def test_detect_anomalies_none(self):
        """Test anomaly detection with healthy battery."""
        report = BatteryReport(self.base_data)
        soh = report.calculate_state_of_health()
        anomalies = report.detect_anomalies(soh)
        
        self.assertEqual(anomalies, [])
    
    def test_detect_anomalies_multiple(self):
        """Test anomaly detection with multiple issues."""
        data = self.base_data.copy()
        data["current_capacity_kwh"] = 45.0  # SoH = 75% (low health)
        data["cells"] = [
            {"id": 0, "voltage": 3.80, "temperature": 48.0},  # Low voltage + overheating
            {"id": 1, "voltage": 4.20, "temperature": 32.0},  # High voltage
        ]
        
        report = BatteryReport(data)
        soh = report.calculate_state_of_health()
        anomalies = report.detect_anomalies(soh)
        
        # Should detect: voltage imbalance, overheating, low health
        self.assertEqual(len(anomalies), 3)
        self.assertIn("Voltage imbalance detected", anomalies)
        self.assertIn("Overheating detected", anomalies)
        self.assertIn("Low State of Health", anomalies)
    
    def test_generate_report_healthy(self):
        """Test full report generation for healthy battery."""
        report_obj = BatteryReport(self.base_data)
        report = report_obj.generate_report()
        
        # Verify structure
        self.assertIn("battery_soh", report)
        self.assertIn("cycle_count", report)
        self.assertIn("anomalies", report)
        
        # Verify values
        self.assertEqual(report["battery_soh"], 90.0)
        self.assertEqual(report["cycle_count"], 300)
        self.assertEqual(report["anomalies"], [])
    
    def test_generate_report_with_anomalies(self):
        """Test full report generation with anomalies."""
        data = self.base_data.copy()
        data["cells"] = [
            {"id": 0, "voltage": 3.80, "temperature": 30.0},
            {"id": 1, "voltage": 4.15, "temperature": 32.0},
        ]
        
        report_obj = BatteryReport(data)
        report = report_obj.generate_report()
        
        # Should detect voltage imbalance (spread = 0.35V)
        self.assertGreater(len(report["anomalies"]), 0)
        self.assertIn("Voltage imbalance detected", report["anomalies"])
    
    def test_empty_cells(self):
        """Test handling of empty cells array (edge case)."""
        data = self.base_data.copy()
        data["cells"] = []
        
        report = BatteryReport(data)
        
        # Should not crash and should return False for detections
        self.assertFalse(report.detect_voltage_imbalance())
        self.assertFalse(report.detect_overheating())


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBatteryReport)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
