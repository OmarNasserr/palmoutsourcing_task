"""
Battery Report Module

Contains the BatteryReport class that processes EV diagnostic data to calculate
State of Health (SoH), detect anomalies, and generate structured reports.
"""

from typing import Dict, List, Any


class BatteryReport:
    """
    Processes battery diagnostic data and generates health reports.
    
    This class implements production-grade battery analysis logic used in
    electric vehicle battery management systems. It calculates key metrics
    and detects anomalies that may indicate battery degradation or safety issues.
    
    Attributes:
        VOLTAGE_IMBALANCE_THRESHOLD: Maximum acceptable voltage difference between cells (V)
        OVERHEATING_THRESHOLD: Maximum safe cell temperature (°C)
        LOW_HEALTH_THRESHOLD: Minimum acceptable State of Health percentage
    """
    
    # Thresholds based on industry standards and safety requirements
    VOLTAGE_IMBALANCE_THRESHOLD = 0.05  # 50mV - typical BMS tolerance
    OVERHEATING_THRESHOLD = 45.0  # °C - lithium-ion safe operating limit
    LOW_HEALTH_THRESHOLD = 80.0  # % - common warranty threshold
    
    def __init__(self, diagnostic_data: Dict[str, Any]):
        """
        Initialize the battery report with diagnostic data.
        
        Args:
            diagnostic_data: Dictionary containing vehicle_id, timestamp, cells,
                           cycle_count, nominal_capacity_kwh, current_capacity_kwh
        """
        self.data = diagnostic_data
        self.cells = diagnostic_data.get("cells", [])
        self.cycle_count = diagnostic_data.get("cycle_count", 0)
        self.nominal_capacity = diagnostic_data.get("nominal_capacity_kwh", 0)
        self.current_capacity = diagnostic_data.get("current_capacity_kwh", 0)
    
    def calculate_state_of_health(self) -> float:
        """
        Calculate the State of Health (SoH) of the battery.
        
        State of Health is the primary metric for battery degradation, comparing
        current capacity to the original nominal capacity. It's expressed as a
        percentage where 100% means no degradation.
        
        Formula: SoH = (current_capacity / nominal_capacity) × 100
        
        Returns:
            float: State of Health as a percentage (0-100)
        
        Note:
            In production systems, SoH calculation may also factor in internal
            resistance, charge acceptance rate, and discharge performance curves.
            This implementation uses capacity-based SoH as it's the most common
            industry standard.
        """
        if self.nominal_capacity == 0:
            return 0.0
        
        soh = (self.current_capacity / self.nominal_capacity) * 100
        return round(soh, 2)
    
    def detect_voltage_imbalance(self) -> bool:
        """
        Detect if there's significant voltage imbalance between cells.
        
        Voltage imbalance occurs when cells in a battery pack drift apart in
        voltage, indicating potential cell degradation, manufacturing defects,
        or thermal management issues. Excessive imbalance can lead to:
        - Reduced pack capacity (limited by weakest cell)
        - Accelerated degradation
        - Safety risks (overcharging weak cells)
        
        Threshold: 50mV (0.05V) is a typical BMS warning threshold.
        Production systems may use 30-100mV depending on chemistry and application.
        
        Returns:
            bool: True if voltage spread exceeds threshold
        """
        if not self.cells:
            return False
        
        voltages = [cell["voltage"] for cell in self.cells]
        voltage_range = max(voltages) - min(voltages)
        
        return voltage_range > self.VOLTAGE_IMBALANCE_THRESHOLD
    
    def detect_overheating(self) -> bool:
        """
        Detect if any cell is exceeding safe operating temperature.
        
        Overheating is a critical safety concern in lithium-ion batteries:
        - Normal operating range: 15-40°C
        - Warning threshold: 45°C (used here)
        - Critical threshold: 60°C (thermal runaway risk)
        
        Causes of overheating:
        - High ambient temperature
        - Insufficient cooling
        - High charge/discharge rates
        - Internal short circuits
        - Cell degradation
        
        Returns:
            bool: True if any cell temperature exceeds safe threshold
        """
        if not self.cells:
            return False
        
        for cell in self.cells:
            if cell["temperature"] > self.OVERHEATING_THRESHOLD:
                return True
        
        return False
    
    def detect_low_health(self, soh: float) -> bool:
        """
        Detect if battery State of Health is below acceptable threshold.
        
        The 80% threshold is industry-standard for several reasons:
        - Most EV warranties guarantee 80% capacity retention
        - Below 80%, users experience noticeable range reduction
        - Degradation often accelerates below this point
        - Many manufacturers consider 70-80% as end-of-first-life
        
        Args:
            soh: State of Health percentage
        
        Returns:
            bool: True if SoH is below threshold
        
        Note:
            In production, this threshold may be configurable per vehicle model
            or adjusted based on customer requirements.
        """
        return soh < self.LOW_HEALTH_THRESHOLD
    
    def detect_anomalies(self, soh: float) -> List[str]:
        """
        Detect all anomalies in the battery diagnostic data.
        
        This method aggregates all anomaly detection checks and returns a list
        of human-readable anomaly descriptions. In production, these would
        typically be logged, sent to monitoring systems, and potentially
        trigger alerts to service teams or customers.
        
        Args:
            soh: Pre-calculated State of Health
        
        Returns:
            List[str]: List of detected anomaly descriptions
        """
        anomalies = []
        
        if self.detect_voltage_imbalance():
            anomalies.append("Voltage imbalance detected")
        
        if self.detect_overheating():
            anomalies.append("Overheating detected")
        
        if self.detect_low_health(soh):
            anomalies.append("Low State of Health")
        
        return anomalies
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive battery health report.
        
        This is the main public method that orchestrates all calculations and
        anomaly detection to produce a structured report suitable for:
        - API responses
        - Database storage
        - Customer dashboards
        - Service technician diagnostics
        
        Returns:
            Dict[str, Any]: Report containing:
                - battery_soh: State of Health percentage
                - cycle_count: Number of charge cycles
                - anomalies: List of detected issues
        
        Example:
            >>> report = BatteryReport(diagnostic_data).generate_report()
            >>> print(report)
            {
                "battery_soh": 91.5,
                "cycle_count": 412,
                "anomalies": ["Voltage imbalance detected"]
            }
        """
        # Calculate State of Health
        soh = self.calculate_state_of_health()
        
        # Detect all anomalies
        anomalies = self.detect_anomalies(soh)
        
        # Build structured report
        report = {
            "battery_soh": soh,
            "cycle_count": self.cycle_count,
            "anomalies": anomalies
        }
        
        return report
