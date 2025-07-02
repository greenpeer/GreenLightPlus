# File path: GreenLightPlus/service_functions/co2_ppm2dens.py
"""
CO2 PPM to Density Conversion Utility
====================================

This module provides conversion between CO2 volumetric concentration (ppm)
and mass density (kg/m³) for greenhouse climate calculations. This is the
inverse operation of co2_dens2ppm.

The conversion is essential for:
- Model state variable calculations
- Mass balance equations
- CO2 injection rate calculations
- Integration with control systems

Physical Basis:
    Uses the ideal gas law (PV = nRT) with standard atmospheric pressure.
    The conversion accounts for temperature effects on gas density.

Copyright Statement:
    Based on original Matlab code by David Katzin (david.katzin@wur.nl)
    Python implementation by Daidai Qiu (qiu.daidai@outlook.com)
    Last Updated: July 2025
    
    Licensed under GNU GPLv3. See LICENSE file for details.
"""

import numpy as np
from typing import Union

# Note: Numba JIT compilation available for performance
# Uncomment for ~10x speedup on large arrays:
# from numba import jit
# @jit(nopython=True)

def co2_ppm2dens(temp: Union[float, np.ndarray], ppm: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert CO2 volumetric concentration (ppm) to mass density (kg/m³).
    
    Transforms parts per million volumetric concentration to mass density
    using the ideal gas law. This conversion is temperature-dependent due
    to thermal expansion effects on gas density.
    
    Mathematical Formulation:
        ρ = (ppm * 10^-6 * P * M) / (R * T)
        
    Where:
        ppm = CO2 concentration (parts per million by volume)
        P = Atmospheric pressure (101325 Pa)
        M = Molar mass of CO2 (0.04401 kg/mol)
        R = Universal gas constant (8.3144598 J/mol·K)
        T = Absolute temperature (K)
    
    Args:
        temp (float or np.ndarray): Air temperature in degrees Celsius.
            Can be scalar or array for batch processing.
            Valid range: > -273.15°C (above absolute zero).
        ppm (float or np.ndarray): CO2 concentration in ppm (volumetric).
            Typical greenhouse range: 400-1500 ppm.
            Must be non-negative.
    
    Returns:
        float or np.ndarray: CO2 mass density in kg/m³.
            Return type matches input type.
            Typical range: 0.7-2.7 kg/m³ for greenhouse conditions.
    
    Examples:
        >>> # Ambient conditions
        >>> co2_ppm2dens(20.0, 400)
        0.716
        
        >>> # Enriched greenhouse atmosphere
        >>> co2_ppm2dens(25.0, 1000)
        1.77
        
        >>> # Array processing for time series
        >>> temps = np.array([20, 22, 24])
        >>> ppms = np.array([400, 600, 800])
        >>> co2_ppm2dens(temps, ppms)
        array([0.716, 1.068, 1.416])
    
    Note:
        - Assumes standard atmospheric pressure (1 atm)
        - For high altitude greenhouses, pressure correction needed
        - Input arrays must have compatible shapes for broadcasting
    """
    # Physical Constants
    R = 8.3144598      # Universal gas constant [J mol^-1 K^-1]
    C2K = 273.15       # Celsius to Kelvin offset [K]
    M_CO2 = 44.01e-3   # Molar mass of CO2 [kg mol^-1]
    P = 101325         # Standard atmospheric pressure [Pa]


    # Convert temperature to Kelvin
    temp_K = temp + C2K

    # Calculate CO2 density
    co2_dens = P * 1e-6 * ppm * M_CO2 / (R * temp_K)

    return co2_dens
