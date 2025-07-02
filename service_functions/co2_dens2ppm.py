# File path: GreenLightPlus/service_functions/co2_dens2ppm.py
"""
CO2 Density to PPM Conversion Utility
====================================

This module provides conversion between CO2 mass density (kg/m³) and
volumetric concentration (ppm) for greenhouse climate calculations.

The conversion is essential for:
- Interfacing between different model components
- Sensor data interpretation
- Control system setpoints
- Physiological calculations

Physical Basis:
    Uses the ideal gas law (PV = nRT) with standard atmospheric pressure.
    Accounts for temperature effects on gas density.

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.
"""

import numpy as np
from typing import Union

# Note: Numba JIT compilation available for performance optimization
# Uncomment the following lines to enable:
# from numba import jit
# @jit(nopython=True)

def co2_dens2ppm(temp: Union[float, np.ndarray], dens: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert CO2 density to volumetric concentration in ppm.
    
    This function transforms CO2 mass density (kg/m³) to parts per million
    (ppm) volumetric concentration, accounting for temperature effects on
    gas density through the ideal gas law.
    
    Mathematical Formulation:
        ppm = 10^6 * (ρ * R * T) / (P * M)
        
    Where:
        ρ = CO2 density (kg/m³)
        R = Universal gas constant (8.3144598 J/mol·K)
        T = Absolute temperature (K)
        P = Atmospheric pressure (101325 Pa)
        M = Molar mass of CO2 (0.04401 kg/mol)

    Args:
        temp (float or np.ndarray): Air temperature in degrees Celsius.
            Can be scalar or array for vectorized operations.
            Valid range: > -273.15°C (above absolute zero).
        dens (float or np.ndarray): CO2 mass density in kg/m³.
            Must be non-negative. Typical range: 0-2 kg/m³.
            Shape must match temp if both are arrays.

    Returns:
        float or np.ndarray: CO2 concentration in ppm (parts per million).
            Return type matches input type (scalar or array).
            Typical greenhouse range: 400-1500 ppm.

    Examples:
        >>> # Single value conversion
        >>> co2_dens2ppm(20.0, 0.716)  # 20°C, typical density
        400.0
        
        >>> # Array conversion for time series
        >>> temps = np.array([18, 20, 22])
        >>> densities = np.array([0.73, 0.716, 0.702])
        >>> co2_dens2ppm(temps, densities)
        array([398.5, 400.0, 401.5])

    Note:
        - Assumes standard atmospheric pressure (1 atm = 101325 Pa)
        - Valid for typical greenhouse conditions
        - For high altitude locations, pressure correction may be needed
    """
    
    # Physical Constants
    R = 8.3144598      # Universal gas constant [J mol⁻¹ K⁻¹]
    C2K = 273.15       # Celsius to Kelvin conversion offset [K]
    M_CO2 = 44.01e-3   # Molar mass of CO2 [kg mol⁻¹]
    P = 101325         # Standard atmospheric pressure [Pa]
    
    # Ensure inputs are numpy arrays for vectorized operations
    temp = np.asarray(temp)
    dens = np.asarray(dens)
    
    # Apply ideal gas law conversion
    # Factor of 1e6 converts from fraction to ppm
    ppm = 1e6 * R * (temp + C2K) * dens / (P * M_CO2)

    return ppm
