"""
Relief amount calculator based on disaster type, severity, and affected area.
"""

from decimal import Decimal
from typing import Optional


# Base relief amounts per disaster type (in USD per square km)
BASE_RELIEF_PER_SQKM = {
    "fire": Decimal("50000"),      # $50k per sq km
    "flood": Decimal("75000"),      # $75k per sq km (more infrastructure damage)
    "crowd": Decimal("10000"),      # $10k per sq km (less infrastructure impact)
}

# Severity multipliers
SEVERITY_MULTIPLIERS = {
    "low": Decimal("0.5"),
    "medium": Decimal("1.0"),
    "high": Decimal("2.0"),
    "critical": Decimal("4.0"),
}

# Population-based relief (per person)
RELIEF_PER_PERSON = {
    "fire": Decimal("500"),
    "flood": Decimal("800"),
    "crowd": Decimal("200"),
}


def calculate_relief_amount(
    incident_type: str,
    severity: str,
    affected_area: Optional[float] = None,
    affected_population: Optional[int] = None,
) -> Decimal:
    """
    Calculate relief amount based on disaster parameters.
    
    Args:
        incident_type: Type of disaster (fire, flood, crowd)
        severity: Severity level (low, medium, high, critical)
        affected_area: Affected area in square kilometers
        affected_population: Number of affected people
        
    Returns:
        Calculated relief amount in USD
    """
    if incident_type not in BASE_RELIEF_PER_SQKM:
        incident_type = "fire"  # Default
    
    if severity not in SEVERITY_MULTIPLIERS:
        severity = "medium"  # Default
    
    multiplier = SEVERITY_MULTIPLIERS[severity]
    base_amount = Decimal("0")
    
    # Calculate based on area if provided
    if affected_area and affected_area > 0:
        area_relief = BASE_RELIEF_PER_SQKM[incident_type] * Decimal(str(affected_area))
        base_amount += area_relief
    
    # Calculate based on population if provided
    if affected_population and affected_population > 0:
        population_relief = RELIEF_PER_PERSON[incident_type] * Decimal(str(affected_population))
        base_amount += population_relief
    
    # If neither area nor population provided, use default estimates
    if base_amount == 0:
        # Default estimates based on severity
        default_area = {
            "low": 0.1,
            "medium": 0.5,
            "high": 2.0,
            "critical": 5.0,
        }.get(severity, 0.5)
        
        default_population = {
            "low": 50,
            "medium": 200,
            "high": 1000,
            "critical": 5000,
        }.get(severity, 200)
        
        area_relief = BASE_RELIEF_PER_SQKM[incident_type] * Decimal(str(default_area))
        population_relief = RELIEF_PER_PERSON[incident_type] * Decimal(str(default_population))
        base_amount = area_relief + population_relief
    
    # Apply severity multiplier
    total_relief = base_amount * multiplier
    
    return total_relief


def estimate_severity_from_confidence(confidence: float) -> str:
    """
    Estimate severity based on detection confidence.
    This is a simple heuristic - can be improved with actual ML model outputs.
    """
    if confidence >= 0.9:
        return "critical"
    elif confidence >= 0.75:
        return "high"
    elif confidence >= 0.5:
        return "medium"
    else:
        return "low"


def estimate_affected_area_from_confidence(
    incident_type: str, confidence: float
) -> float:
    """
    Estimate affected area based on confidence and incident type.
    Higher confidence might indicate larger/more visible disasters.
    """
    # Base area estimates (sq km)
    base_areas = {
        "fire": 0.5,
        "flood": 2.0,
        "crowd": 0.1,
    }
    
    base_area = base_areas.get(incident_type, 0.5)
    
    # Scale by confidence (higher confidence = potentially larger area)
    estimated_area = base_area * confidence * 2
    
    return max(0.1, estimated_area)  # Minimum 0.1 sq km
